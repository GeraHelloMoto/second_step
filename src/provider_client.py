import httpx
from datetime import date, datetime
from typing import Optional, Dict, Any, List
from src.config import settings
import logging

logger = logging.getLogger(__name__)

class EventsProviderClient:
    def __init__(self, mock: bool = None):
        if mock is None:
            mock = settings.use_mock_provider

        self.mock = mock
        if not mock:
            self.base_url = settings.provider_base_url
            self.api_key = settings.provider_api_key
            self.headers = {"x-api-key": self.api_key}
        else:
            logger.warning("Using MOCK provider client – no real API calls")

    async def _request(self, method: str, path: str, **kwargs) -> Dict[str, Any]:
        if self.mock:
            raise NotImplementedError("Mock does not implement _request")
        async with httpx.AsyncClient(base_url=self.base_url, follow_redirects=True, timeout=30.0) as client:
            response = await client.request(method, path, headers=self.headers, **kwargs)
            response.raise_for_status()
            return response.json()

    async def get_events_page(self, changed_at: date, cursor: Optional[str] = None) -> Dict[str, Any]:
        if self.mock:
            # if not hasattr(self, "_mock_returned"):
            #     self._mock_returned = True
                return {
                "next": None,
                "results": [
                    {
                        "id": "11111111-1111-1111-1111-111111111111",
                        "name": "Mock Conference 1",
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
                    },
                    {
                        "id": "22222222-2222-2222-2222-222222222222",
                        "name": "Mock Conference 2",
                        "place": {
                            "id": "p2",
                            "name": "Another Place",
                            "city": "SPb",
                            "address": "Nevsky 2",
                            "seats_pattern": "B1-20"
                        },
                        "event_time": "2026-11-15T14:00:00+03:00",
                        "registration_deadline": "2026-11-14T14:00:00+03:00",
                        "status": "published",
                        "number_of_visitors": 0,
                        "changed_at": "2026-01-02T10:00:00+03:00",
                        "created_at": "2026-01-02T10:00:00+03:00",
                        "status_changed_at": "2026-01-02T10:00:00+03:00"
                    }
                ]
            }
        
            
        url = f"/api/events/?changed_at={changed_at.isoformat()}"
        if cursor:
            url += f"&cursor={cursor}"
        return await self._request("GET", url)

    async def get_available_seats(self, event_id: str) -> List[str]:
        if self.mock:
            return ["A1", "A2", "A3", "B1", "B2", "C1"]
        # raise NotImplementedError
        data = await self._request("GET", f"/api/events/{event_id}/seats/")
        return data["seats"]

    async def register(self, event_id: str, first_name: str, last_name: str, email: str, seat: str) -> str:
        if self.mock:
            return "mock-ticket-id-123"
        # raise NotImplementedError
        payload = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "seat": seat,
        }
        data = await self._request("POST", f"/api/events/{event_id}/register/", json=payload)
        return data["ticket_id"]

    async def unregister(self, event_id: str, ticket_id: str) -> bool:
        if self.mock:
            return True
        payload = {"ticket_id": ticket_id}
        await self._request("DELETE", f"/api/events/{event_id}/unregister/", json=payload)
        return True
        # raise NotImplementedError