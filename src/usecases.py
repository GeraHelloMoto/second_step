import logging
from datetime import date, datetime

from cachetools import TTLCache

from src.paginator import EventsPaginator
from src.provider_client import EventsProviderClient
from src.repositories import EventRepository, SyncMetadataRepository, TicketRepository
from src.schemas import EventResponse, PlaceSchema

logger = logging.getLogger(__name__)

class SyncEventsUsecase:
    def __init__(
        self,
        client: EventsProviderClient,
        event_repo: EventRepository,
        sync_repo: SyncMetadataRepository
    ):
        self.client = client
        self.event_repo = event_repo
        self.sync_repo = sync_repo

    async def sync(self) -> None:
        logger.info("Starting sync")
        meta = await self.sync_repo.get()
        if meta and meta.last_changed_at:
            changed_at_date = meta.last_changed_at.date()
        else:
            changed_at_date = date(2000, 1, 1)

        paginator = EventsPaginator(self.client, changed_at_date)
        max_changed_at = None

        async for events_batch in paginator:
            for ev in events_batch:
                place = ev["place"]

                def parse_datetime(value):
                    if isinstance(value, datetime):
                        return value
                    return datetime.fromisoformat(value.replace('Z', '+00:00'))

                event_data = {
                    "id": ev["id"],
                    "name": ev["name"],
                    "place_id": place["id"],
                    "place_name": place["name"],
                    "place_city": place["city"],
                    "place_address": place["address"],
                    "seats_pattern": place["seats_pattern"],
                    "event_time": parse_datetime(ev["event_time"]),
                    "registration_deadline":parse_datetime(ev["registration_deadline"]),
                    "status": ev["status"],
                    "number_of_visitors": ev["number_of_visitors"],
                    "changed_at": parse_datetime(ev["changed_at"]),
                    "created_at": parse_datetime(ev["created_at"]),
                    "status_changed_at": parse_datetime(ev["status_changed_at"]),
                }
                await self.event_repo.upsert(event_data)

                ts = event_data["changed_at"]
                if max_changed_at is None or ts > max_changed_at:
                    max_changed_at = ts

        now = datetime.now()
        last_changed = max_changed_at or (datetime.now() if meta is None \
         else meta.last_changed_at)
        await self.sync_repo.update(now, last_changed, "success")
        logger.info("Sync finished")

class GetEventsUsecase:
    def __init__(self, event_repo: EventRepository):
        self.event_repo = event_repo

    async def execute(
        self,
        date_from: date | None,page: int,
        page_size: int
        ) -> tuple[list[EventResponse], int]:
        offset = (page - 1) * page_size
        events,total=await self.event_repo.list_with_filters(date_from,offset,page_size)
        result = []
        for ev in events:
            result.append(EventResponse(
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
        return result, total

class GetEventDetailUsecase:
    def __init__(self, event_repo: EventRepository):
        self.event_repo = event_repo

    async def execute(self, event_id: str) -> EventResponse | None:
        event = await self.event_repo.get_by_id(event_id)
        if not event:
            return None
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

class GetSeatsUsecase:
    def __init__(self,client: EventsProviderClient,maxsize: int = 1000, ttl: int =30):
        self.client = client
        self.cache = TTLCache(maxsize=maxsize, ttl=ttl)

    async def execute(self, event_id: str) -> list[str]:
        if event_id in self.cache:
            return self.cache[event_id]
        seats = await self.client.get_available_seats(event_id)
        self.cache[event_id] = seats
        return seats

class CreateTicketUsecase:
    def __init__(self,
        client: EventsProviderClient,
        event_repo: EventRepository,
        ticket_repo: TicketRepository
    ):
        self.client = client
        self.event_repo = event_repo
        self.ticket_repo = ticket_repo

    async def execute(self,
        event_id: str,
        first_name: str,
        last_name: str,
        email: str,
        seat: str
    ) -> str:
        event = await self.event_repo.get_by_id(event_id)
        if not event:
            raise ValueError("Event not found")
        if event.status != "published":
            raise ValueError("Registration is not available for this event")

        now = datetime.now(event.event_time.tzinfo)
        if now > event.registration_deadline:
            raise ValueError("Registration deadline has passed")
        ticket_id=await self.client.register(event_id,first_name,last_name,email,seat)
        await self.ticket_repo.create(ticket_id,
            event_id,first_name,
            last_name,email,seat
        )
        return ticket_id

class CancelTicketUsecase:
    def __init__(
        self,
        client: EventsProviderClient,
        ticket_repo: TicketRepository,
        event_repo: EventRepository
    ):
        self.client = client
        self.ticket_repo = ticket_repo
        self.event_repo = event_repo

    async def execute(self, ticket_id: str) -> bool:
        ticket = await self.ticket_repo.get(ticket_id)
        if not ticket:
            raise ValueError("Ticket not found")
        await self.client.unregister(ticket.event_id, ticket_id)
        await self.ticket_repo.delete(ticket_id)
        return True
