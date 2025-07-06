from typing import List
from pydantic import BaseModel, Field, ConfigDict
from pydantic.alias_generators import to_camel


class CharacterBase(BaseModel):
    """Base character schema with common fields"""
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True  # replaces orm_mode=True
    )
    id: int
    name: str
    height: str | None = None
    mass: str | None = None

class CharacterCreate(BaseModel):
    """Schema for creating a character"""
    name: str = Field(..., example="John Doe")
    height: str | None = Field(None, example="172")
    mass: str | None = Field(None, example="77")
    film_ids: List[int] = Field(default_factory=list, example=[1, 2])
    starship_ids: List[int] = Field(default_factory=list, example=[3])

class CharacterRead(CharacterBase):
    """Schema for reading character data with relationships"""
    films: List['FilmBase'] = Field(..., description="List of films the character appeared in")
    starships: List['StarshipBase'] = Field(..., description="List of starships the character piloted")

# Resolve circular references by importing after class definition
from app.schemas.film import FilmBase
from app.schemas.starship import StarshipBase
CharacterRead.model_rebuild()

# Pagination helper type for character responses
from app.schemas.pagination import PaginatedResponse
PaginatedCharacters = PaginatedResponse[CharacterRead]
