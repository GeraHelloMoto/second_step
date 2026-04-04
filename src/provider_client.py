import httpx
from datetime import date
from typing import Optional, Dict, Any, List
from src.config import settings
import logging

logger = logging.getLogger(__name__)

class EventsProviderClient:
    def __init__(self, mock: bool = False):
        self.mock = mock
        if not mock:
            self.base_url = settings.provider_base_url
            self.api_key = settings.provider_api_key
            self.headers = {"x-api-key": self.api_key}
        else:
            logger.warning("Using MOCK provider client – no real API calls")

    async def _request(self, method: str, path: str, **kwargs) -> Dict[str, Any]:
        if self.mock:
           
            if "events" in path and "seats" not in path:
                return {"next": None, "results": []}
            elif "seats" in path:
                return {"seats": ["A1", "A2", "B1"]}
            elif "register" in path:
                return {"ticket_id": "mock-ticket-id"}
            elif "unregister" in path:
                return {"success": True}
            else:
                return {}
        async with httpx.AsyncClient(base_url=self.base_url, timeout=30.0) as client:
            response = await client.request(method, path, headers=self.headers, **kwargs)
            response.raise_for_status()
            return response.json()

    async def get_events_page(self, changed_at: date, cursor: Optional[str] = None) -> Dict[str, Any]:
        
        if self.mock:
            return {"next": None, "results": []}
        params = {"changed_at": changed_at.isoformat()}
        url = f"/api/events/?changed_at={changed_at.isoformat()}"
        if cursor:
            url += f"&cursor={cursor}"
        return await self._request("GET", url)

    async def get_available_seats(self, event_id: str) -> List[str]:
        if self.mock:
            return ["A1", "A2", "B1"]
        data = await self._request("GET", f"/api/events/{event_id}/seats/")
        return data["seats"]

    async def register(self, event_id: str, first_name: str, last_name: str, email: str, seat: str) -> str:
        if self.mock:
            return "mock-ticket-id"
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