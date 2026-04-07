import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.dependencies import get_provider_client
from src.provider_client import EventsProviderClient
from src.repositories import EventRepository, SyncMetadataRepository
from src.usecases import SyncEventsUsecase

router = APIRouter(prefix="/api/sync", tags=["sync"])
logger = logging.getLogger(__name__)

@router.post("/trigger")
async def trigger_sync(
    db: AsyncSession = Depends(get_db),
    client: EventsProviderClient = Depends(get_provider_client)
):
    try:
        event_repo = EventRepository(db)
        sync_repo = SyncMetadataRepository(db)
        usecase = SyncEventsUsecase(client, event_repo, sync_repo)
        await usecase.sync()
        await db.commit()
        return {"status": "sync triggered successfully"}
    except Exception as e:
        await db.rollback()
        logger.exception("Sync failed")
        raise HTTPException(status_code=500, detail=str(e))
