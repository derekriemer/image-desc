from typing import List, Optional, Union
from pydantic import BaseModel, Field, ValidationError


class Entity(BaseModel):
    category: str
    name: str
    description: Optional[str] = None


class Context(BaseModel):
    entities: List[Entity] = Field(default_factory=list)
    setting: str = Field(default_factory=str)
