import abc
import json
import shutil
import uuid
from dataclasses import is_dataclass, asdict
from pathlib import Path
from typing import Type, Optional, Tuple, Iterable, Any
from typing import TypeVar
from filelock import FileLock


def saveable(cls=None, /, field_as_id: str = 'id'):
    def wrapper(cls):
        def my_id_or_default(self):
            __default_id__ = '__default_id__'
            if hasattr(self, field_as_id):
                if getattr(self, field_as_id, None) is None:
                    setattr(self, field_as_id, str(uuid.uuid4()))
                return getattr(self, field_as_id)
            elif hasattr(self, '__loaded_id__'):
                setattr(self, __default_id__, getattr(self, '__loaded_id__'))
            elif getattr(self, __default_id__, None) is None:
                setattr(self, __default_id__, str(uuid.uuid4()))
            return getattr(self, __default_id__)

        setattr(cls, '__my_id__', my_id_or_default)
        if not hasattr(cls, '__json__'):
            if is_dataclass(cls):
                setattr(cls, '__json__',
                        lambda self:
                            json.dumps(
                                asdict(self),
                                separators=(',', ':')
                            )
                        )
            elif is_pydantic(cls):
                setattr(cls, '__json__', lambda self: self.model_dump_json())
            else:
                raise NotImplementedError(
                    f'The class {cls} is not @dataclass nor Pydantic Model and does not have __json__() method.'
                    f'Please implement __json__() method by yourself.')
        return cls

    if cls is None:
        return wrapper
    else:
        return wrapper(cls)


def is_pydantic(cls):
    return any(filter(lambda c: c.__name__ == 'BaseModel', cls.__mro__))


StoredModel = TypeVar('StoredModel')
RelatedModel = TypeVar('RelatedModel')


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
             *related_model: RelatedModel | Tuple[RelatedModel, str]) -> Any:
        """
        Save model.

        :param model: A model.
        :param related_model: Related model(s) -- model that the stored model is belong to.
        :return Returns saved model id
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
                    path /= FileStorage._get_model_path(model.__class__, model.__my_id__())

        return path / model_class.__name__ / model_id

    def _prepare_file(self, model_class: Type[StoredModel], model_id: str,
                      *related_model: RelatedModel | Tuple[RelatedModel, str]):
        path = self.base_path / FileStorage._get_model_path(model_class, model_id, *related_model).with_suffix('.json')
        lock = path.with_suffix('.lock')
        path.parent.mkdir(parents=True, exist_ok=True)
        return path, FileLock(lock)

    def save(self, model: StoredModel,
             *related_model: RelatedModel | Tuple[RelatedModel, str]) -> Any:
        model_id = model.__my_id__()
        path, lock = self._prepare_file(model.__class__, model_id, *related_model)
        with lock:
            with path.open('w', encoding='UTF-8') as f:
                f.write(model.__json__())
                return model_id

    def load(self, model_class: Type[StoredModel], model_id: str,
             *related_model: RelatedModel | Tuple[RelatedModel, str]) -> Optional[StoredModel]:
        path, lock = self._prepare_file(model_class, model_id, *related_model)
        with lock:
            if not path.exists():
                return None
            with open(path, 'r') as f:
                content = json.load(f)
            if is_pydantic(model_class):
                model = model_class.model_validate(content)
            else:
                model = model_class(**content)
            setattr(model, '__loaded_id__', model_id)
            return model

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


__all__ = ('saveable', 'storage', )
