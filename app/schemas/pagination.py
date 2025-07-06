from typing import Generic, TypeVar, List
from pydantic import ConfigDict
from pydantic.alias_generators import to_camel
from pydantic.generics import GenericModel

T = TypeVar("T")

class PaginatedResponse(GenericModel, Generic[T]):
    """
    Generic pagination schema to wrap lists of items with total count.
    Uses Pydantic generics for flexible typing.
    """
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True
    )
    total: int
    items: List[T]
