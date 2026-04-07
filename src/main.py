import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api import db_check, events, health, seats, sync, tickets
from src.background.sync_worker import shutdown_scheduler, start_scheduler
from src.config import settings
from src.database import engine
from src.models import Base

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created!😎")
    start_scheduler(settings.sync_interval_hours)
    yield
    await shutdown_scheduler()
    await engine.dispose()

app = FastAPI(lifespan=lifespan)

app.include_router(health.router)
app.include_router(db_check.router)
app.include_router(events.router)
app.include_router(seats.router)
app.include_router(tickets.router)
app.include_router(sync.router)

