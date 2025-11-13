# app/main.py

from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.db import get_db

# This is the ASGI application Uvicorn loads
app = FastAPI(title="SuperStatsFootball backend")

@app.get("/")
def root():
    return {"message": "SuperStatsFootball backend running!"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/db-version")
def db_version(db: Session = Depends(get_db)):
    """
    Simple endpoint to test connection to Supabase Postgres.
    """
    # SQLAlchemy 2.x: wrap raw SQL in text()
    result = db.execute(text("SELECT version()"))
    version = result.scalar()
    return {"db_version": version}
