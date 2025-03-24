from typing import List
from pydantic import BaseModel


class Description(BaseModel):
    short: str
    people: List[str]
    long_description: str


class Entities(BaseModel):
    people: List[str]
    objects: List[str]
