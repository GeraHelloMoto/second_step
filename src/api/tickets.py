from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.dependencies import get_provider_client
from src.provider_client import EventsProviderClient
from src.repositories import EventRepository, TicketRepository
from src.schemas import SuccessResponse, TicketCreateRequest, TicketResponse
from src.usecases import CancelTicketUsecase, CreateTicketUsecase

router = APIRouter(prefix="/api/tickets", tags=["tickets"])

@router.post("", status_code=201)
async def create_ticket(
    req: TicketCreateRequest,
    db: AsyncSession = Depends(get_db),
    client: EventsProviderClient = Depends(get_provider_client)
):
    event_repo = EventRepository(db)
    ticket_repo = TicketRepository(db)
    usecase = CreateTicketUsecase(client, event_repo, ticket_repo)
    try:
        ticket_id = await usecase.execute(
            req.event_id, req.first_name, req.last_name, req.email, req.seat
        )
        await db.commit()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return TicketResponse(ticket_id=ticket_id)

@router.delete("/{ticket_id}")
async def cancel_ticket(
    ticket_id: str,
    db: AsyncSession = Depends(get_db),
    client: EventsProviderClient = Depends(get_provider_client)
):
    ticket_repo = TicketRepository(db)
    event_repo = EventRepository(db)
    usecase = CancelTicketUsecase(client, ticket_repo, event_repo)
    try:
        await usecase.execute(ticket_id)
        await db.commit()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return SuccessResponse(success=True)
