from typing import List
from dataclasses import dataclass
from pydantic import


@dataclass
class Description(Model):
    short: str
    people: List[str]
    long_description: str


@dataclass
class Entities:
    people: List[str]
    objects: List[str]
