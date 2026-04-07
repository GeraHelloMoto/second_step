from src.provider_client import EventsProviderClient, RealEventsProviderClient


def get_provider_client() -> EventsProviderClient:

    return RealEventsProviderClient()
