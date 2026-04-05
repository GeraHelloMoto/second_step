import asyncio
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
from src.database import AsyncSessionLocal
from src.repositories import EventRepository, SyncMetadataRepository
from src.provider_client import EventsProviderClient
from src.usecases import SyncEventsUsecase


logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()

async def run_sync():
	logger.info("Background sync started at %s", datetime.now())
	async with AsyncSessionLocal() as db:
		client = EventsProviderClient()
		event_repo = EventRepository()
		sync_repo = SyncMetadataRepository(db)
		usecase = SyncEventsUsecase(client, event_repo, sync_repo)
		try:
			await usecase.sync()
			await db.commit()
		except Exception as e:
			await db.rollback()
			logger.exception("Background sync failed: %s", e)


def start_scheduler(interval_hours: int):
	scheduler.add_job(run_sync, "interval", hours=interval_hours, next_run_time=datetime.now())
	scheduler.start()

async def shutdown_scheduler():
	scheduler.shutdown()				