from typing import List, Optional, Union
from pydantic import BaseModel, Field, ValidationError


class Entity(BaseModel):
    category: str
    name: str
    description: str


class Context(BaseModel):
    entities: List[Entity]
    setting: Optional[str] = None
