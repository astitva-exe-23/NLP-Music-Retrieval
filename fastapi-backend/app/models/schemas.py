from typing import List, Optional, Literal
from pydantic import BaseModel

class DiaryFilters(BaseModel):
    language: Optional[str] = None
    explicit: Optional[bool] = None
    era: Optional[str] = None

class DiaryRequest(BaseModel):
    diary_text: str
    k: int = 10
    filters: Optional[DiaryFilters] = None

class Facets(BaseModel):
    mood: Optional[str] = None
    topics: List[str] = []
    energy: Optional[Literal["low","med","high"]] = None
    language_pref: Optional[str] = None
    era: Optional[str] = None
    query_string: str

class Track(BaseModel):
    id: str
    title: str
    artist: str
    language: Optional[str] = None
    score: float

class RecommendationResponse(BaseModel):
    items: List[Track]
    trace: dict
