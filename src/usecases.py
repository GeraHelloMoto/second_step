import logging
from datetime import datetime, date
from src.repositories import EventRepository, SyncMetadataRepository
from src.provider_client import EventsProviderClient
from src.paginator import EventsPaginator

logger = logging.getLogger(__name__)

class SyncEventsUsecase:
    def __init__(self, client: EventsProviderClient, event_repo: EventRepository, sync_repo: SyncMetadataRepository):
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
                event_data = {
                    "id": ev["id"],
                    "name": ev["name"],
                    "place_id": place["id"],
                    "place_name": place["name"],
                    "place_city": place["city"],
                    "place_address": place["address"],
                    "seats_pattern": place["seats_pattern"],
                    "event_time": ev["event_time"],
                    "registration_deadline": ev["registration_deadline"],
                    "status": ev["status"],
                    "number_of_visitors": ev["number_of_visitors"],
                    "changed_at": ev["changed_at"],
                    "created_at": ev["created_at"],
                    "status_changed_at": ev["status_changed_at"],
                }
                await self.event_repo.upsert(event_data)
                # Отслеживаем максимальное changed_at
                ts = ev["changed_at"]
                if max_changed_at is None or ts > max_changed_at:
                    max_changed_at = ts

        now = datetime.now()
        last_changed = max_changed_at or (datetime.now() if meta is None else meta.last_changed_at)
        await self.sync_repo.update(now, last_changed, "success")
        logger.info("Sync finished")