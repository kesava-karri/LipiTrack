# seed_data.py
import random
from datetime import date, datetime, timedelta

from database import SessionLocal, engine, Base
import models

# Ensure tables exist
Base.metadata.create_all(bind=engine)


def create_demo_user(db):
    user = db.query(models.User).filter(
        models.User.email == "demo@example.com").first()
    if user:
        return user
    user = models.User(email="demo@example.com",
                       hashed_password="demo123", full_name="Demo User")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def random_lab_results(db, user, months=12, points=8):
    base_date = date.today()
    results = []
    for i in range(points):
        days_back = int((months*30) * (i / (points-1)))  # spread over months
        test_date = base_date - timedelta(days=days_back)
        # create some trending-ish values
        ldl = round(140 - i*3 + random.uniform(-5, 5), 1)
        hdl = round(45 + random.uniform(-3, 3), 1)
        total = round(ldl + hdl + random.uniform(10, 30), 1)
        triglycerides = round(130 + random.uniform(-20, 40), 1)
        non_hdl = round(total - hdl, 1)
        lr = models.LabResult(
            user_id=user.id,
            test_date=test_date,
            total_cholesterol=total,
            ldl=ldl,
            hdl=hdl,
            triglycerides=triglycerides,
            non_hdl=non_hdl,
            notes="Auto-seeded",
            created_at=datetime.utcnow()
        )
        db.add(lr)
        results.append(lr)
    db.commit()
    for r in results:
        db.refresh(r)
    return results


def random_daily_habits(db, user, days=60):
    items = []
    for d in range(days):
        entry_date = date.today() - timedelta(days=d)
        exercise = random.choice([0, 15, 30, 45, 60])
        diet_score = random.choices(
            [1, 2, 3, 4, 5], weights=[5, 10, 40, 30, 15])[0]
        smoked = random.random() < 0.05
        alcohol = random.random() < 0.15
        dh = models.DailyHabit(
            user_id=user.id,
            entry_date=entry_date,
            sleep_hours=round(random.uniform(5.5, 8.5), 1),
            exercise_minutes=exercise,
            diet_score=diet_score,
            smoked=smoked,
            alcohol=alcohol,
            notes="seed"
        )
        db.add(dh)
        items.append(dh)
    db.commit()
    for i in items:
        db.refresh(i)
    return items


def main():
    db = SessionLocal()
    try:
        user = create_demo_user(db)
        random_lab_results(db, user)
        random_daily_habits(db, user, days=90)
        print("Seeded demo user id:", user.id)
    finally:
        db.close()


if __name__ == "__main__":
    main()
