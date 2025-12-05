from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Using SQLite file for now
SQLALCHEMY_DATABASE_URL = "sqlite:///./lipitrack.db"

engine = create_engine(
  SQLALCHEMY_DATABASE_URL,
  connect_args={"check_same_thread": False} # required for SQLite + FastAPI
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Add DB session to each request & close automatically

def get_db():
  db = SessionLocal()
  try:
    yield db
  finally:
    db.close()
