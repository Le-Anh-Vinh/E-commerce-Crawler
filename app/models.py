from typing import List, Optional
from pydantic import BaseModel

class Location(BaseModel):
    longitude: float
    latitude: float
    address: str
    district: Optional[str]
    city: Optional[str]
    country: Optional[str]

class Room(BaseModel):
    name: str
    description: Optional[str]
    capacity: int
    beds: int
    rating: Optional[float]
    longitude: float
    latitude: float
    category_id: int
    crawl_room_id: int
    host_id: Optional[int] = None
    images: List[str] = []
    amenities: List[str] = []
