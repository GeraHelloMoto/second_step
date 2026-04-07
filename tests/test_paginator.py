from datetime import date
from unittest.mock import AsyncMock

import pytest

from src.paginator import EventsPaginator
from tests.mock_provider_client import MockEventsProviderClient


@pytest.mark.asyncio
async def test_paginator_yields_pages():

    mock_client = MockEventsProviderClient()

    mock_client.get_events_page = AsyncMock(side_effect=[
        {"next": "?cursor=abc", "results": [{"id": 1}]},
        {"next": None, "results": [{"id": 2}]},
    ])
    paginator = EventsPaginator(mock_client, date(2026, 1, 1))
    pages = []
    async for page in paginator:
        pages.append(page)
    assert len(pages) == 2
    assert pages[0] == [{"id": 1}]
    assert pages[1] == [{"id": 2}]
    assert mock_client.get_events_page.call_count == 2

@pytest.mark.asyncio
async def test_paginator_stops_when_no_next():
    mock_client = MockEventsProviderClient()
    mock_client.get_events_page = AsyncMock(return_value={"next": None, "results": []})
    paginator = EventsPaginator(mock_client, date(2026, 1, 1))
    pages = []
    async for page in paginator:
        pages.append(page)
    assert len(pages) == 1
    assert pages[0] == []
