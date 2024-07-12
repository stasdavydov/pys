from pydantic import BaseModel

from . import saveable


@saveable(field_as_id='id')
class ModelWithID(BaseModel):
    """
    Base class for models with `id` field prefilled with random UUID if not initialized.
    """
    id: str = None
