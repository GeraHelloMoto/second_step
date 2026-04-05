from datetime import date, datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Event, SyncMetadata, Ticket


class EventRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, event_data: Dict[str, Any]) -> Event:
        event = Event(**event_data)
        self.session.add(event)
        await self.session.flush()
        return event

    async def upsert(self, event_data: Dict[str, Any]) -> None:
        stmt = select(Event).where(Event.id == event_data["id"])
        result = await self.session.execute(stmt)
        existing = result.scalar_one_or_none()
        if existing:
            for key, value in event_data.items():
                setattr(existing, key, value)
        else:
            new_event = Event(**event_data)
            self.session.add(new_event)

    async def get_by_id(self, event_id: str) -> Optional[Event]:
        return await self.session.get(Event, event_id)

    async def list_all(
        self, offset: int = 0, limit: int = 20
    ) -> tuple[List[Event], int]:
        query = select(Event).order_by(Event.event_time).offset(offset).limit(limit)
        result = await self.session.execute(query)
        events = result.scalars().all()
        count_query = select(func.count()).select_from(Event)
        total = await self.session.scalar(count_query)
        return events, total or 0

    async def delete_all(self) -> None:
        await self.session.execute(Event.__table__.delete())

    async def list_with_filters(
        self, date_from: Optional[date], offset: int, limit: int
    ) -> tuple[List[Event], int]:
        query = select(Event)
        if date_from:
            start_datetime = datetime.combine(date_from, datetime.min.time())
            query = query.where(Event.event_time >= start_datetime)
        count_query = select(func.count()).select_from(query.subquery())
        total = await self.session.scalar(count_query)
        query = query.order_by(Event.event_time).offset(offset).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all(), total or 0


class SyncMetadataRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self) -> Optional[SyncMetadata]:
        stmt = select(SyncMetadata).order_by(SyncMetadata.id.desc()).limit(1)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update(
        self, last_sync_time: datetime, last_changed_at: datetime, status: str
    ):
        meta = await self.get()
        if not meta:
            meta = SyncMetadata()
            self.session.add(meta)
        meta.last_sync_time = last_sync_time
        meta.last_changed_at = last_changed_at
        meta.status = status


class TicketRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        ticket_id: str,
        event_id: str,
        first_name: str,
        last_name: str,
        email: str,
        seat: str,
    ):
        ticket = Ticket(
            id=ticket_id,
            event_id=event_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            seat=seat,
        )
        self.session.add(ticket)

    async def get(self, ticket_id: str) -> Optional[Ticket]:
        return await self.session.get(Ticket, ticket_id)

    async def delete(self, ticket_id: str):
        ticket = await self.get(ticket_id)
        if ticket:
            await self.session.delete(ticket)
