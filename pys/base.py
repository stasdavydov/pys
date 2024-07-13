import abc
from typing import TypeVar, Union, Tuple, Type, Optional, Any, Iterable

StoredModel = TypeVar('StoredModel')
RelatedModel = TypeVar('RelatedModel')
Related = Union[RelatedModel, Tuple[RelatedModel, str]]


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
