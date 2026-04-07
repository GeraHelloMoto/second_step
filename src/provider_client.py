import logging
from datetime import date
from typing import Any, Protocol

import httpx

from src.config import settings

logger = logging.getLogger(__name__)

class EventsProviderClient(Protocol):

    async def get_events_page(
        self,
        changed_at: date,
        cursor: str | None = None
    ) -> dict[str, Any]:
        raise NotImplementedError

    async def get_available_seats(self, event_id: str) -> list[str]:
        raise NotImplementedError

    async def register(
        self,
        event_id: str,
        first_name: str,
        last_name: str,
        email: str,
        seat: str
    ) -> str:
        raise NotImplementedError

    async def unregister(self, event_id: str, ticket_id: str) -> bool:
        raise NotImplementedError


class RealEventsProviderClient:
    def __init__(self):
        self.base_url = settings.provider_base_url
        self.api_key = settings.provider_api_key
        self.headers = {"x-api-key": self.api_key}

    async def _request(
        self,
        method: str,
        path: str,
        **kwargs
    ) -> dict[str, Any]:
        async with httpx.AsyncClient(
            base_url=self.base_url,
            follow_redirects=True,
            timeout=30.0
        ) as client:
            response=await client.request(method, path, headers=self.headers, **kwargs)
            response.raise_for_status()
            return response.json()

    async def get_events_page(
        self,
        changed_at: date,
        cursor: str | None = None
    ) -> dict[str, Any]:
        url = f"/api/events/?changed_at={changed_at.isoformat()}"
        if cursor:
            url += f"&cursor={cursor}"
        return await self._request("GET", url)

    async def get_available_seats(self, event_id: str) -> list[str]:
        data = await self._request("GET", f"/api/events/{event_id}/seats/")
        return data["seats"]

    async def register(
        self,
        event_id: str,
        first_name: str,
        last_name: str,
        email: str,
        seat: str
        ) -> str:
        payload = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "seat": seat,
        }
        data=await self._request(
            "POST",
            f"/api/events/{event_id}/register/",
            json=payload
        )
        return data["ticket_id"]

    async def unregister(self, event_id: str, ticket_id: str) -> bool:
        payload = {"ticket_id": ticket_id}
        await self._request("DELETE",f"/api/events/{event_id}/unregister/",json=payload)
        return True
