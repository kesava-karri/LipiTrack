from pydantic import BaseModel, EmailStr
from datetime import date, datetime
from typing import Optional


class UserBase(BaseModel):
    email: EmailStr
    full_name: str | None = None


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: int

    class Config:
        orm_mode = True


class LabResultBase(BaseModel):
    test_date: date
    total_cholesterol: Optional[float] = None
    ldl: Optional[float] = None
    hdl: Optional[float] = None
    triglycerides: Optional[float] = None
    non_hdl: Optional[float] = None
    notes: Optional[str] = None


class LabResultCreate(LabResultBase):
    pass


class LabResultRead(LabResultBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        orm_mode = True


class DailyHabitBase(BaseModel):
    entry_date: date
    sleep_hours: Optional[float] = None
    exercise_minutes: Optional[int] = None
    diet_score: Optional[int] = None  # 1-5
    smoked: Optional[bool] = None
    alcohol: Optional[bool] = None
    notes: Optional[str] = None


class DailyHabitCreate(DailyHabitBase):
    pass


class DailyHabitRead(DailyHabitBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        orm_mode = True
