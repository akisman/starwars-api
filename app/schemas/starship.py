from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
from pydantic.alias_generators import to_camel


class StarshipBase(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True
    )
    id: int
    name: str
    model: Optional[str] = None
    starship_class: Optional[str] = None

class StarshipCreate(BaseModel):
    """Schema for creating a character"""
    name: str = Field(..., example="Serenity")
    model: str | None = Field(None, example="Firefly")
    starship_class: str | None = Field(None, example="Multipurpose, Mid-Bulk Transport")
    film_ids: List[int] = Field(default_factory=list, example=[1, 2])
    character_ids: List[int] = Field(default_factory=list, example=[1])

class StarshipRead(StarshipBase):
    """Schema for reading starship data with relationships"""
    films: List['FilmBase'] = Field(..., description="List of films the character appeared in")
    characters: List['CharacterBase'] = Field(..., description="List of characters the character appeared in")

# Resolve circular references by importing after class definition
from app.schemas.film import FilmBase, CharacterBase
StarshipRead.model_rebuild()

# Pagination helper type for character responses
from app.schemas.pagination import PaginatedResponse
PaginatedStarships = PaginatedResponse[StarshipRead]
