from datetime import date, timedelta
from fastapi import Depends, Form, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List

import models
import schemas
from auth_utils import hash_password, verify_password, create_access_token
from database import engine, Base, get_db

Base.metadata.create_all(bind=engine)

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# To allow local dev frontend (Vite) calls to the backend
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        sub = payload.get("sub")
        if sub is None:
            raise credentials_exception
        token_data = TokenData(user_id=int(sub))
    except (JWTError, ValueError):
        raise credentials_exception

    user = db.query(models.User).filter(
        models.User.id == token_data.user_id).first()
    if user is None:
        raise credentials_exception
    return user


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "message": "LipiTrack backend is running"
    }


@app.post("/auth/login", response_model=schemas.Token)
def login(
    payload: schemas.LoginRequest,
    db: Session = Depends(get_db),
):
    user = db.query(models.User).filter(
        models.User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # create JWT with user id in "sub"
    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me", response_model=schemas.UserRead)
async def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user


@app.post("/users/", response_model=schemas.UserRead, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(
        models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    new_user = models.User(
        email=user.email,
        hashed_password=hash_password(user.password),
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
def create_lab_result(
    payload: schemas.LabResultCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    user = db.query(models.User).filter(
        models.User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    lr = models.LabResult(
        user_id=current_user.id,
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
def create_daily_habit(
    payload: schemas.DailyHabitCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(
        models.User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    dh = models.DailyHabit(
        user_id=current_user.id,
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
def list_daily_habits(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    results = db.query(models.DailyHabit).filter(
        models.DailyHabit.user_id == current_user.id).order_by(models.DailyHabit.entry_date.desc()).all()
    return results


@app.get("/me/summary/", response_model=schemas.UserSummary)
def my_summary(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return build_user_summary(db, current_user.id)


@app.get("/users/{user_id}/summary/", response_model=schemas.UserSummary)
def user_summary(user_id: int, db: Session = Depends(get_db)):
    return build_user_summary(db, user_id)


def build_user_summary(db: Session, user_id: int) -> schemas.UserSummary:
    if not user_id:
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

    return schemas.UserSummary(summary)
