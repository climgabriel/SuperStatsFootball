from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.db import get_db

# This must exist at module level, with this exact name
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
    Simple test endpoint to confirm Supabase Postgres connection.
    """
    version = db.execute("SELECT version()").scalar()
    return {"db_version": version}
