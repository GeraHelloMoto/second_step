from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List, Dict, Any 
from src.models import Event, SyncMetadata
from datetime import datetime


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

	async def get_by_id(self, event_id: str) -> Otional[Event]:
		return await self.session.get(Event, event_id)

	async def list_all(self, offset: int = 0, limit: int = 20) -> tuple[List[Event], int]:
		query = select(Event).order_by(Event.event_time).offset(offset).limit(limit)
		result = await self.session.execute(query)
		events = result.scalars().all()
		count_query = select(func.count()).select_from(Event)
		total = await self.session.scalar(count_query)
		return events, total or 0

	async def delete_all(self) -> None:
		await self.session.execute(Event.__table__.delete())
		



class SyncMetadataRepository:
	def __init__(self, session: AsyncSession):
		self.session = session 

	async def get(self) -> Optional[SyncMetadata]:
		stmt = select(SyncMetadata).order_by(SyncMetadata.id.desc()).limit(1)
		result = await self.session.execute(stmt)
		return result.scalar_one_or_none()

	async def update(self, last_sync_time: datetime, last_changed_at: datetime, status: str):
		meta = await self.get()
		if not meta:
			meta = SyncMetadata()
			self.session.add(meta)
		meta.last_sync_time = last_sync_time
		meta.last_changed_at = last_changed_at
		meta.status = status