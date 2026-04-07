import logging
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from src.database import AsyncSessionLocal
from src.dependencies import get_provider_client
from src.repositories import EventRepository, SyncMetadataRepository
from src.usecases import SyncEventsUsecase

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()

async def run_sync():
    logger.info("Background sync started at %s", datetime.now())
    async with AsyncSessionLocal() as db:
        client = get_provider_client()
        event_repo = EventRepository(db)
        sync_repo = SyncMetadataRepository(db)
        usecase = SyncEventsUsecase(client, event_repo, sync_repo)
        try:
            await usecase.sync()
            await db.commit()
        except Exception as e:
            await db.rollback()
            logger.exception("Background sync failed: %s", e)

def start_scheduler(interval_hours: int):
    scheduler.add_job(
        run_sync,
        "interval",
        hours=interval_hours,
        next_run_time=datetime.now()
    )
    scheduler.start()

async def shutdown_scheduler():
    scheduler.shutdown()
