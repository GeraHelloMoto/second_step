from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.api import health, db_check
from src.database import engine
from src.models import Base
import logging



logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created!😎")
    except Exception as e:
        logger.error(f"Failed to create database tables!😥 {e}")
        logger.warning("App will continue but DB features may not work!")
    yield
    await engine.dispose()

app = FastAPI(lifespan=lifespan)
app.include_router(health.router)
app.include_router(db_check.router)
