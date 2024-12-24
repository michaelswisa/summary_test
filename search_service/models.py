from datetime import datetime
from typing import Optional, List, Literal
from pydantic import BaseModel, Field

class Location(BaseModel):
    lat: float
    lon: float

class GeoFilter(BaseModel):
    lat: float
    lon: float
    distance: str = Field(description="Distance in km (e.g., '10km')")

class SearchParams(BaseModel):
    query: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: Optional[int] = 100
    source: Optional[Literal["historic", "news"]] = None
    category: Optional[str] = None
    geo_filter: Optional[GeoFilter] = None
    sort_by: Optional[Literal["date", "relevance"]] = "relevance"
    sort_order: Optional[Literal["asc", "desc"]] = "desc"

class SearchResult(BaseModel):
    id: str
    title: Optional[str]
    body: str
    date: Optional[datetime]
    location: Optional[Location]
    source: str
    category: Optional[str]
    score: Optional[float] = None

class SearchResponse(BaseModel):
    total: int
    results: List[SearchResult]
    aggregations: Optional[dict] = None 