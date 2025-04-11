import logging
from csv import DictReader

from api.context import Context

logger = logging.getLogger(__name__)


def load_context(setting: str):
    # For the prototype, hardcode context.csv. I will be using a context builder for this for the real app.
    with open("context.csv", "r", encoding="utf-8") as f:
        reader = DictReader(f)
        entities = list(reader)
        return Context(setting=setting, entities=entities)
