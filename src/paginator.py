from datetime import date
from typing import AsyncIterator, Dict, Any, Optional
from src.provider_client import EventsProviderClient


class EventsPaginator:
	def __init__(self, client: EventsProviderClient, changed_at: date):
		self.client = client 
		self.changed_at = changed_at
		self._next_cursor: Optional[str] = None
		self._finished = False

	def __aiter__(self):
		return self

	async def __anext__(self) -> Dict[str, Any]:
		if self._finished:
			raise StopAsyncIteration
		page = await self.client.get_events_page(self.changed_at, self._next_cursor)
		results = page.get("results", [])
		next_url = page.get("next")
		if next_url:
			from urllib.parse import urlparse, parse_qs
			parsed = urlparse(next_url)
			query = parse_qs(parsed.query)
			self._next_cursor = query.get("cursor", [None])[0]
		else:
			self._finished = True
		return results