from api.context import Context
from csv import DictReader


def load_context():
    # For the prototype, hardcode context.csv. I will be using a context builder for this for the real app.
    with open("context.csv", "r", encoding="utf-8") as f:
        reader = DictReader(f)
        entities = list(reader)
        return Context(setting="An adaptive ice climbing outing at the Vail Ampatheator. There were about 13 people. About 1/2 of the people were adaptive atheletes, the rest were guides or volunteers.", entities=entities)
