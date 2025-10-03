# app/db/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Define the location of our SQLite database file
SQLALCHEMY_DATABASE_URL = "sqlite:///./app/data/audit.db"

# The connect_args is needed only for SQLite to allow multi-threaded access
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# SessionLocal will be the class we use to create database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    Dependency function to get a database session for a single request.
    Ensures the session is always closed after the request is finished.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
