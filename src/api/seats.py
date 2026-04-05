import time

from fastapi import APIRouter, HTTPException

from src.config import settings
from src.provider_client import EventsProviderClient

router = APIRouter(prefix="/api/events", tags=["seats"])


_cache = {}
TTL = settings.cache_seats_ttl


@router.get("/{event_id}/seats")
async def get_available_seats(event_id: str):

    now = time.time()
    if event_id in _cache:
        ts, seats = _cache[event_id]
        if now - ts < TTL:
            return {"event_id": event_id, "available_seats": seats}

    client = EventsProviderClient()
    try:
        seats = await client.get_available_seats(event_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    _cache[event_id] = (now, seats)
    return {"event_id": event_id, "available_seats": seats}
