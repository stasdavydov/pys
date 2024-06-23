import abc
import shutil
import uuid
from pathlib import Path
from typing import Any, TypeVar
from typing import Type, Optional, Tuple, Iterable

from filelock import FileLock
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


StoredModel = TypeVar('StoredModel', bound=ModelWithID)
RelatedModel = TypeVar('RelatedModel', bound=ModelWithID)


class BaseStorage(abc.ABC):
    """
    Abstract base storage
    """
    def load(self, model_class: Type[StoredModel], model_id: str,
             *related_model: RelatedModel | Tuple[RelatedModel, str]) \
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
             *related_model: RelatedModel | Tuple[RelatedModel, str]) -> None:
        """
        Save model.

        :param model: A model.
        :param related_model: Related model(s) -- model that the stored model is belong to.
        """
        raise NotImplementedError

    def delete(self, model_class: Type[StoredModel], model_id: str,
               *related_model: RelatedModel | Tuple[RelatedModel, str]) -> None:
        """
        Delete model.

        :param model_class: Model class.
        :param model_id: Model ID.
        :param related_model: Related model(s) -- model that the deleted model is belong to.
        """
        raise NotImplementedError

    def list(self, model_class: Type[StoredModel],
             *related_model: RelatedModel | Tuple[RelatedModel, str]) -> Iterable[StoredModel]:
        """
        List models.
        :param model_class: Model class
        :param related_model: Related model(s) -- model that the listed models are belong to.
        :return: List of found models.
        """
        raise NotImplementedError


class FileStorage(BaseStorage):
    """
    File based storage implementation. Thread and interprocess safe.
    """
    base_path: Path

    def __init__(self, base_path: str | Path) -> None:
        """
        Base path for the storage files
        :param base_path: base path.
        """
        self.base_path = base_path if isinstance(base_path, Path) else Path(base_path)

    @staticmethod
    def _get_model_path(model_class: Type[StoredModel], model_id: str,
                        *related_model: RelatedModel | Tuple[Type[RelatedModel], str]) -> Path:
        path = Path()
        if not related_model:
            path /= ''
        else:
            for model in related_model:
                if isinstance(model, tuple):
                    path /= FileStorage._get_model_path(*model)
                else:
                    path /= FileStorage._get_model_path(model.__class__, model.id)

        return path / model_class.__name__ / model_id

    def _prepare_file(self, model_class: Type[StoredModel], model_id: str,
                      *related_model: RelatedModel | Tuple[RelatedModel, str]):
        path = self.base_path / FileStorage._get_model_path(model_class, model_id, *related_model).with_suffix('.json')
        lock = path.with_suffix('.lock')
        path.parent.mkdir(parents=True, exist_ok=True)
        return path, FileLock(lock)

    def save(self, model: StoredModel,
             *related_model: RelatedModel | Tuple[RelatedModel, str]) -> None:
        path, lock = self._prepare_file(model.__class__, model.id, *related_model)
        with lock:
            with path.open('w', encoding='UTF-8') as f:
                f.write(model.json())

    def load(self, model_class: Type[StoredModel], model_id: str,
             *related_model: RelatedModel | Tuple[RelatedModel, str]) -> Optional[StoredModel]:
        path, lock = self._prepare_file(model_class, model_id, *related_model)
        with lock:
            if not path.exists():
                return None
            return model_class.parse_file(path)

    def delete(self, model_class: Type[StoredModel], model_id: str,
               *related_model: RelatedModel | Tuple[RelatedModel, str]) -> None:
        path, lock = self._prepare_file(model_class, model_id, *related_model)
        with lock:
            path.unlink(missing_ok=True)
            sub_path = path.with_suffix('')
            if sub_path.exists():
                shutil.rmtree(sub_path)

    def list(self, model_class: Type[StoredModel],
             *related_model: RelatedModel | Tuple[RelatedModel, str]) -> Iterable[StoredModel]:

        path, lock = self._prepare_file(model_class, '__list__', *related_model)
        with lock:
            for p in path.parent.glob('*.json'):
                yield self.load(model_class, p.with_suffix('').name, *related_model)

    def __str__(self) -> str:
        return f'file.Storage(base_path={self.base_path})'


def storage(base_path: str | Path):
    return FileStorage(base_path)


__all__ = ('ModelWithID', 'storage', )
