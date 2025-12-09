from sqlalchemy import Column, Integer, String, Date, Float, Text, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship

from database import Base
from datetime import datetime, timezone


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)


class LabResult(Base):
    __tablename__ = "lab_results"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    test_date = Column(Date, nullable=False)

    total_cholesterol = Column(Float, nullable=True)
    ldl = Column(Float, nullable=True)
    hdl = Column(Float, nullable=True)
    triglycerides = Column(Float, nullable=True)
    non_hdl = Column(Float, nullable=True)

    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

    user = relationship("User", backref="lab_results")


class DailyHabit(Base):
    __tablename__ = "daily_habits"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    entry_date = Column(Date, nullable=False)

    sleep_hours = Column(Float, nullable=True)
    exercise_minutes = Column(Integer, nullable=True)
    diet_score = Column(Integer, nullable=True)  # 1-5
    smoked = Column(Boolean, nullable=True)
    alcohol = Column(Boolean, nullable=True)

    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

    user = relationship("User", backref="daily_habits")
