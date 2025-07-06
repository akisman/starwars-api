from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from pydantic.alias_generators import to_camel


class FilmBase(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True
    )
    id: int
    title: str
    episode_id: int
    opening_crawl: Optional[str] = None
    director: Optional[str] = None
    producer: Optional[str] = None
    release_date: Optional[str] = None

class FilmCreate(BaseModel):
    """Schema for creating a film"""
    title: str = Field(..., example="Yet Another Star Wars Movie")
    episode_id: int = Field(..., example=500)
    opening_crawl: str | None = Field(None, example="In a galaxy far, far away...")
    director: str | None = Field(None, example="George Lucas")
    producer: str | None = Field(None, example="George Lucas")
    release_date: str | None = Field(None, example="2025-07-06")
    character_ids: List[int] = Field(default_factory=list, example=[1])
    starship_ids: List[int] = Field(default_factory=list, example=[3])

class FilmRead(FilmBase):
    """Schema for reading film data with relationships"""
    characters: List['CharacterBase'] = Field(..., description='List of characters')
    starships: List['StarshipBase'] = Field(..., description="List of starships")

# Resolve circular references by importing after class definition
from app.schemas.character import CharacterBase
from app.schemas.starship import StarshipBase
FilmRead.model_rebuild()

# Pagination helper type for character responses
from app.schemas.pagination import PaginatedResponse
PaginatedFilms = PaginatedResponse[FilmRead]
