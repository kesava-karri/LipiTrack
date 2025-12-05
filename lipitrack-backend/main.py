from typing import List

from fastapi import FastAPI, Depends, HTTPException, status
from sqlmodel import Session

from database import engine, Base, get_db
import models, schemas

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
  existing_user = db.query(models.User).filter(models.User.email == user.email).first()
  if existing_user:
    raise HTTPException(
      status_code=status.HTTP_400_BAD_REQUEST,
      detail="Email already registered",
    )

  # TODO: hash password properly later
  new_user = models.User(
    email=user.email,
    hashed_password=user.password, #placeholder
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
