from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db
from src.repositories import EventRepository
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import uuid
from src.schemas import EventListResponse, EventResponse, PlaceSchema


router = APIRouter(prefix="/api/events", tags=["events"])

class EventCreate(BaseModel):
    name: str
    place_id: str
    place_name: str
    place_city: str
    place_address: str
    seats_pattern: str
    event_time: datetime
    registration_deadline: datetime
    status: str = "published"
    number_of_visitors: int = 0
    changed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    status_changed_at: Optional[datetime] = None

@router.post("/manual", status_code=201)
async def create_event_manual(data: EventCreate, db: AsyncSession = Depends(get_db)):
    
    repo = EventRepository(db)
    event_id = str(uuid.uuid4())
    now = datetime.now()
    event_data = data.dict()
    event_data["id"] = event_id
    event_data["changed_at"] = event_data.get("changed_at") or now
    event_data["created_at"] = event_data.get("created_at") or now
    event_data["status_changed_at"] = event_data.get("status_changed_at") or now
    event = await repo.create(event_data)
    await db.commit()
    return {"id": event.id, "name": event.name}

@router.get("")
async def list_events(
    date_from: Optional[date] = Query(None, description="Filter events after this date (YYYY-MM-DD)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db)
):
    repo = EventRepository(db)
    offset = (page - 1) * page_size
    events, total = await repo.list_with_filters(date_from, offset, page_size)

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

    
    results = []
    for ev in events:
        results.append(EventResponse(
            id=ev.id,
            name=ev.name,
            place=PlaceSchema(
                id=ev.place_id,
                name=ev.place_name,
                city=ev.place_city,
                address=ev.place_address,
                seats_pattern=ev.seats_pattern,
            ),
            event_time=ev.event_time,
            registration_deadline=ev.registration_deadline,
            status=ev.status,
            number_of_visitors=ev.number_of_visitors,
            )) 
    return EventListResponse(count=total, next=next_url, previous=prev_url, results=results)

@router.get("/{event_id}")
async def get_event(event_id: str, db: AsyncSession = Depends(get_db)):
    repo = EventRepository(db)
    event = await repo.get_by_id(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return EventResponse(
        id=event.id,
        name=event.name,
        place=PlaceSchema(
            id=event.place_id,
            name=event.place_name,
            city=event.place_city,
            address=event.place_address,
            seats_pattern=event.seats_pattern,
        ),
        event_time=event.event_time,
        registration_deadline=event.registration_deadline,
        status=event.status,
        number_of_visitors=event.number_of_visitors,
    )                   