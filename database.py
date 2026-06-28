from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Support DATABASE_URL (Render standard) or individual env vars (Docker local)
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    SQLALCHEMY_DATABASE_URL = DATABASE_URL
else:
    DB_USER = os.getenv("POSTGRES_USER", "bi_user")
    DB_PASS = os.getenv("POSTGRES_PASSWORD", "bi_password")
    DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
    DB_PORT = os.getenv("POSTGRES_PORT", "5432")
    DB_NAME = os.getenv("POSTGRES_DB", "bi_db")
    SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Readonly uses the same connection (no separate readonly user on Render)
engine_readonly = engine
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
