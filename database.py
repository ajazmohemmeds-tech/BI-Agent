from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

DB_USER = os.getenv("POSTGRES_USER", "bi_user")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "bi_password")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_NAME = os.getenv("POSTGRES_DB", "bi_db")

SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:5432/{DB_NAME}"
READONLY_DATABASE_URL = f"postgresql://bi_readonly:readonly_password@{DB_HOST}:5432/{DB_NAME}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

engine_readonly = create_engine(READONLY_DATABASE_URL)
SessionReadOnly = sessionmaker(autocommit=False, autoflush=False, bind=engine_readonly)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_readonly_db():
    db = SessionReadOnly()
    try:
        yield db
    finally:
        db.close()
