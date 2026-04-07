from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.repositories import EventRepository
from src.schemas import EventListResponse
from src.usecases import GetEventDetailUsecase, GetEventsUsecase

router = APIRouter(prefix="/api/events", tags=["events"])

@router.get("")
async def list_events(
    date_from: date | None = Query(None,
    description="Filter events after this date (YYYY-MM-DD)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db)
):
    repo = EventRepository(db)
    usecase = GetEventsUsecase(repo)
    events, total = await usecase.execute(date_from, page, page_size)

    base_url = "/api/events"
    next_url = None
    prev_url = None
    if page * page_size < total:
        next_url = f"{base_url}?page={page+1}&page_size={page_size}"
        if date_from:
            next_url += f"&date_from={date_from.isoformat()}"
    if page > 1:
        prev_url = f"{base_url}?page={page-1}&page_size={page_size}"
        if date_from:
            prev_url += f"&date_from={date_from.isoformat()}"

    return EventListResponse(
        count=total,
        next=next_url,
        previous=prev_url,
        results=events
    )

@router.get("/{event_id}")
async def get_event(
    event_id: str,
    db: AsyncSession = Depends(get_db)
):
    repo = EventRepository(db)
    usecase = GetEventDetailUsecase(repo)
    event = await usecase.execute(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event
