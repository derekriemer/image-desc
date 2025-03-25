import re
from typing import List

from pydantic import BaseModel


class Description(BaseModel):
    title: str
    people: List[str]
    long_description: str

    @property
    def fileName(self):
        return re.sub(r"[^a-zA-Z0-9._- ]", " ", self.title)


class Entities(BaseModel):
    people: List[str]
    objects: List[str]
