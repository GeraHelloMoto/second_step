import uuid
from datetime import date
from typing import Any


class MockEventsProviderClient:

    async def get_events_page(self,
     changed_at: date,
      cursor: str | None = None) -> dict[str, Any]:
        return {
            "next": None,
            "results": [
                {
                    "id": "11111111-1111-1111-1111-111111111111",
                    "name": "Mock Event",
                    "place": {
                        "id": "p1",
                        "name": "Mock Place",
                        "city": "Moscow",
                        "address": "Mock Street 1",
                        "seats_pattern": "A1-10"
                    },
                    "event_time": "2026-12-31T18:00:00+03:00",
                    "registration_deadline": "2026-12-30T18:00:00+03:00",
                    "status": "published",
                    "number_of_visitors": 0,
                    "changed_at": "2026-01-01T10:00:00+03:00",
                    "created_at": "2026-01-01T10:00:00+03:00",
                    "status_changed_at": "2026-01-01T10:00:00+03:00"
                }
            ]
        }

    async def get_available_seats(self, event_id: str) -> list[str]:
        return ["A1", "A2", "A3", "B1", "B2", "C1"]

    async def register(
        self, event_id: str,
         first_name: str,
          last_name: str,
           email: str, seat: str) -> str:
        return str(uuid.uuid4())

    async def unregister(self, event_id: str, ticket_id: str) -> bool:
        return True
