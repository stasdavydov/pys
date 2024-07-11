import uuid

from pydantic import BaseModel

from . import saveable


@saveable(field_as_id='id', default_id=lambda _: str(uuid.uuid4()))
class ModelWithID(BaseModel):
    """
    Base class for models with `id` field prefilled with random UUID if not initialized.
    """
    id: str = None
