from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class PlaceSchema(BaseModel):
    id: str
    name: str
    city: str
    address: str
    seats_pattern: Optional[str] = None


class EventResponse(BaseModel):
    id: str
    name: str
    place: PlaceSchema
    event_time: datetime
    registration_deadline: datetime
    status: str
    number_of_visitors: int


class EventListResponse(BaseModel):
    count: int
    next: Optional[str] = None
    previous: Optional[str] = None
    results: List[EventResponse]


class TicketCreateRequest(BaseModel):
    event_id: str
    first_name: str
    last_name: str
    email: str
    seat: str


class TicketResponse(BaseModel):
    ticket_id: str


class SuccessResponse(BaseModel):
    success: bool
