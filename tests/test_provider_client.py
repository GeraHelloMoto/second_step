from datetime import date

import pytest

from tests.mock_provider_client import MockEventsProviderClient


@pytest.mark.asyncio
async def test_mock_client_returns_events():
    client = MockEventsProviderClient()
    result = await client.get_events_page(date(2000, 1, 1))
    assert "results" in result
    assert len(result["results"]) > 0
    assert "id" in result["results"][0]

@pytest.mark.asyncio
async def test_mock_client_seats():
    client = MockEventsProviderClient()
    seats = await client.get_available_seats("any-id")
    assert isinstance(seats, list)
    assert len(seats) > 0

@pytest.mark.asyncio
async def test_mock_client_register():
    client = MockEventsProviderClient()
    ticket_id = await client.register("event1", "Ivan", "Ivanov", "i@i.ru", "A1")
    assert ticket_id is not None
    assert isinstance(ticket_id, str)

@pytest.mark.asyncio
async def test_mock_client_unregister():
    client = MockEventsProviderClient()
    result = await client.unregister("event1", "ticket1")
    assert result is True
