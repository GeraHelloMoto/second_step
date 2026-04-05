from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.provider_client import EventsProviderClient
from src.repositories import EventRepository, TicketRepository
from src.schemas import SuccessResponse, TicketCreateRequest, TicketResponse

router = APIRouter(prefix="/api/tickets", tags=["tickets"])

@router.post("", status_code=201)
async def create_ticket(
    req: TicketCreateRequest,
    db: AsyncSession = Depends(get_db)
):
    event_repo = EventRepository(db)
    event = await event_repo.get_by_id(req.event_id)
    if not event:

        raise HTTPException(status_code=400, detail="Event not found")
    if event.status != "published":
        raise HTTPException(status_code=400, detail="Registration is \
         not available for this event")
    now = datetime.now(event.event_time.tzinfo)
    if now > event.registration_deadline:
        raise HTTPException(status_code=400, detail="Registration deadline has passed")

    client = EventsProviderClient()
    try:
        ticket_id = await client.register(
            req.event_id, req.first_name, req.last_name, req.email, req.seat
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    ticket_repo = TicketRepository(db)
    await ticket_repo.create(
        ticket_id, req.event_id, req.first_name, req.last_name, req.email, req.seat
    )
    await db.commit()
    return TicketResponse(ticket_id=ticket_id)

@router.delete("/{ticket_id}")
async def cancel_ticket(ticket_id: str, db: AsyncSession = Depends(get_db)):
    ticket_repo = TicketRepository(db)
    ticket = await ticket_repo.get(ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    client = EventsProviderClient()
    try:
        await client.unregister(ticket.event_id, ticket_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    await ticket_repo.delete(ticket_id)
    await db.commit()
    return SuccessResponse(success=True)
