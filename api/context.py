from typing import List, Optional, Union
from pydantic import BaseModel, Field, ValidationError


class Entity(BaseModel):
    category: str
    name: str
    description: Optional[str] = None


class Context(BaseModel):
    entities: List[Entity] = Field(default_factory=list)
    setting: str = Field(default_factory=str)

    def add(self, item: Union[Entity, str]):
        """Add an entity or setting to the context, raising an error if validation fails."""
        if isinstance(item, Entity):
            self.entities.append(item)
        elif isinstance(item, Setting):
            self.settings.append(item)
        else:
            raise TypeError("Item must be an instance of Entity or Setting")


# Example usage
if __name__ == "__main__":
    context = Context()

    # Adding a valid entity
    try:
        context.add(Entity(category="person", name="Alice",
                    description="A person wearing a red dress."))
        print("Entity added successfully!")
    except ValidationError as e:
        print(f"Failed to add entity: {e}")

    # Adding a valid setting
    try:
        context.add(Setting(category="environment",
                    description="A casual dinner setting."))
        print("Setting added successfully!")
    except ValidationError as e:
        print(f"Failed to add setting: {e}")

    # Adding an invalid entity (missing category)
    try:
        context.add(Entity(category="", name="Bob",
                    description="A person with no category."))
    except ValidationError as e:
        print(f"Failed to add entity: {e}")

    # Adding an invalid setting (missing category)
    try:
        context.add(
            Setting(category="", description="An invalid setting with no category."))
    except ValidationError as e:
        print(f"Failed to add setting: {e}")
