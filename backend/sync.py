import asyncio
from app.db.session import SessionLocal
from app.services.data_sync_service import run_full_sync

db = SessionLocal()
try:
    asyncio.run(run_full_sync(db, tier="free"))  # set tier=None to sync everything
finally:
    db.close()