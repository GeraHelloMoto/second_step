import httpx
from fastapi import APIRouter, Depends, HTTPException

from src.config import settings
from src.dependencies import get_provider_client
from src.provider_client import EventsProviderClient
from src.usecases import GetSeatsUsecase

router = APIRouter(prefix="/api/events", tags=["seats"])

@router.get("/{event_id}/seats")
async def get_available_seats(
    event_id: str,
    client: EventsProviderClient = Depends(get_provider_client)
):
    usecase = GetSeatsUsecase(client, maxsize=1000, ttl=settings.cache_seats_ttl)
    try:
        seats = await usecase.execute(event_id)
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail="Event not found")
        raise HTTPException(status_code=500, detail=str(e))
    return {"event_id": event_id, "available_seats": seats}
