from typing import List
from datetime import date, timedelta
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from database import engine, Base, get_db
import models
import schemas

Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "message": "LipiTrack backend is running"
    }


@app.post("/users/", response_model=schemas.UserRead, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(
        models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # TODO: hash password properly later
    new_user = models.User(
        email=user.email,
        hashed_password=user.password,  # placeholder
        full_name=user.full_name,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@app.get("/users/", response_model=List[schemas.UserRead])
def list_users(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    return users


@app.post("/lab-results/", response_model=schemas.LabResultRead, status_code=status.HTTP_201_CREATED)
def create_lab_result(user_id: int, payload: schemas.LabResultCreate, db: Session = Depends(get_db)):
    # In real app, we'd use current user, for now we accept user_id param
    # TODO: Validate the user after implementing auth

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    lr = models.LabResult(
        user_id=user_id,
        test_date=payload.test_date,
        total_cholesterol=payload.total_cholesterol,
        ldl=payload.ldl,
        hdl=payload.hdl,
        triglycerides=payload.triglycerides,
        non_hdl=payload.non_hdl,
        notes=payload.notes,
    )
    db.add(lr)
    db.commit()
    db.refresh(lr)
    return lr


@app.get("/users/{user_id}/lab-results", response_model=List[schemas.LabResultRead])
def list_lab_results(user_id: int, db: Session = Depends(get_db)):
    results = db.query(models.LabResult).filter(
        models.LabResult.user_id == user_id).order_by(models.LabResult.test_date.desc()).all()
    return results


@app.post("/daily-habits/", response_model=schemas.DailyHabitRead, status_code=status.HTTP_201_CREATED)
def create_daily_habit(user_id: int, payload: schemas.DailyHabitCreate, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    dh = models.DailyHabit(
        user_id=user_id,
        entry_date=payload.entry_date,
        sleep_hours=payload.sleep_hours,
        exercise_minutes=payload.exercise_minutes,
        diet_score=payload.diet_score,
        smoked=payload.smoked,
        alcohol=payload.alcohol,
        notes=payload.notes,
    )
    db.add(dh)
    db.commit()
    db.refresh(dh)
    return dh


@app.get("/users/{user_id}/daily_habits/", response_model=List[schemas.DailyHabitRead])
def list_daily_habits(user_id: int, db: Session = Depends(get_db)):
    results = db.query(models.DailyHabit).filter(
        models.DailyHabit.user_id == user_id).order_by(models.DailyHabit.entry_date.desc()).all()
    return results


@app.get("/users/{user_id}/summary/")
def user_summary(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 1) Latest lab result (by test_date)
    latest = (
        db.query(models.LabResult)
        .filter(models.LabResult.user_id == user_id)
        .order_by(models.LabResult.test_date.desc())
        .first()
    )

    # 2) Last 5 lab results for trend (ordered oldest -> newest)
    last5 = (
        db.query(models.LabResult)
        .filter(models.LabResult.user_id == user_id)
        .order_by(models.LabResult.test_date.desc())
        .limit(5)
        .all()
    )

    last5 = list(reversed(last5))

    # 3) Recent habits: 30-day averages
    since = date.today() - timedelta(days=30)
    agg = (
        db.query(
            func.avg(models.DailyHabit.diet_score).label("avg_diet_score"),
            func.avg(models.DailyHabit.exercise_minutes).label(
                "avg_exercise_minutes"),
            func.avg(models.DailyHabit.sleep_hours).label("avg_sleep_hours"),
            func.count(models.DailyHabit.id).label("entries_count"),
        )
        .filter(models.DailyHabit.user_id == user_id)
        .filter(models.DailyHabit.entry_date >= since)
        .one()
    )

    summary = {
        "user_id": user_id,
        "latest_lab": latest,
        "trend_last5": last5,
        "last_30_days": {
            "avg_diet_score": float(agg.avg_diet_score) if agg.avg_diet_score else None,
            "avg_exercise_minutes": float(agg.avg_exercise_minutes) if agg.avg_diet_score else None,
            "avg_sleep_hours": float(agg.avg_sleep_hours) if agg.avg_sleep_hours else None,
            "entries_count": int(agg.entries_count),
        },
    }

    return summary
