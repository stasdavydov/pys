import uuid
from typing import Any

from pydantic import BaseModel


class ModelWithID(BaseModel):
    """
    Base class for models with `id` field prefilled with random UUID if not initialized.
    """
    id: str = None

    def __init__(self, **data: Any) -> None:
        """
        Initialize a model
        :param data: model fields
        """
        super().__init__(**data)
        if self.id is None:
            self.id = str(uuid.uuid4())

    def __my_id__(self):
        return self.id

    def __json__(self):
        return self.model_dump_json()
