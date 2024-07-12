import abc
from typing import TypeVar, Union, Tuple, Type, Optional, Any, Iterable

import msgspec

StoredModel = TypeVar('StoredModel')
RelatedModel = TypeVar('RelatedModel')
Related = Union[RelatedModel, Tuple[RelatedModel, str]]


def is_dataclass(cls):
    import dataclasses
    return dataclasses.is_dataclass(cls)


def is_pydantic(cls):
    try:
        from pydantic import BaseModel
        return issubclass(cls, BaseModel)
    except Exception as e:
        return False


def is_msgspec_struct(cls):
    try:
        import msgspec
        return issubclass(cls, msgspec.Struct)
    except:
        return False


class BaseStorage(abc.ABC):
    """
    Abstract base storage
    """
    def load(self, model_class: Type[StoredModel], model_id: str,
             *related_model: Related) \
            -> Optional[StoredModel]:
        """
        Load model.

        :param model_class: Class of the model.
        :param model_id: Model ID.
        :param related_model: Related model(s) -- model that the loaded model is belong to.
        :return: Loaded model or None in case if model is not found.
        """
        raise NotImplementedError

    def save(self, model: StoredModel,
             *related_model: Related) -> Any:
        """
        Save model.

        :param model: A model.
        :param related_model: Related model(s) -- model that the stored model is belong to.
        :return Returns saved model id
        """
        raise NotImplementedError

    def delete(self, model_class: Type[StoredModel], model_id: str,
               *related_model: Related) -> None:
        """
        Delete model.

        :param model_class: Model class.
        :param model_id: Model ID.
        :param related_model: Related model(s) -- model that the deleted model is belong to.
        """
        raise NotImplementedError

    def list(self, model_class: Type[StoredModel],
             *related_model: Related) -> Iterable[StoredModel]:
        """
        List models.
        :param model_class: Model class
        :param related_model: Related model(s) -- model that the listed models are belong to.
        :return: List of found models.
        """
        raise NotImplementedError

    def destroy(self) -> None:
        """
        Destroy storage
        """
        raise NotImplementedError

    @staticmethod
    def _load(model_class: Type[StoredModel], raw_content, model_id):
        content = msgspec.json.decode(raw_content)
        if is_pydantic(model_class):
            model = model_class.model_validate(content)
        else:
            model = model_class(**content)
            if hasattr(model, '__my_saved_id__'):
                model.__my_saved_id__ = model_id
        return model
