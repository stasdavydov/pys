import os
import shutil
from pathlib import Path
from typing import Type, Optional, Tuple, Iterable, Any, Union

from filelock import FileLock

from .base import BaseStorage, StoredModel, RelatedModel, Related


class Storage(BaseStorage):
    """
    File based storage implementation. Thread and interprocess safe.
    """
    base_path: Path

    def __init__(self, base_path: Union[str, Path]) -> None:
        """
        Base path for the storage files
        :param base_path: base path.
        """
        self.base_path = base_path if isinstance(base_path, Path) else Path(base_path)

    @staticmethod
    def _get_model_path(model_class: Type[StoredModel], model_id: str,
                        *related_model: Union[RelatedModel, Tuple[Type[RelatedModel], str]]) -> Path:
        path = Path()
        if not related_model:
            path /= ''
        else:
            for model in related_model:
                if isinstance(model, tuple):
                    path /= Storage._get_model_path(*model)
                else:
                    path /= Storage._get_model_path(model.__class__, model.__my_id__())

        return path / model_class.__name__ / model_id

    def _prepare_file(self, model_class: Type[StoredModel], model_id: str,
                      *related_model: Related):
        path = self.base_path / Storage._get_model_path(model_class, model_id, *related_model).with_suffix('.json')
        lock = path.with_suffix('.lock')
        path.parent.mkdir(parents=True, exist_ok=True)
        return path, FileLock(lock)

    def save(self, model: StoredModel,
             *related_model: Related) -> Any:
        model_id = model.__my_id__()
        path, lock = self._prepare_file(model.__class__, model_id, *related_model)
        with lock:
            path.write_text(model.__json__(), encoding='utf-8')
            return model_id

    def load(self, model_class: Type[StoredModel], model_id: str,
             *related_model: Related) -> Optional[StoredModel]:
        path, lock = self._prepare_file(model_class, model_id, *related_model)
        with lock:
            if not path.exists():
                return None
            return model_class.__factory__(path.read_text(encoding='utf-8'), model_id)

    def delete(self, model_class: Type[StoredModel], model_id: str,
               *related_model: Related) -> None:
        path, lock = self._prepare_file(model_class, model_id, *related_model)
        with lock:
            path.unlink(missing_ok=True)
            sub_path = path.with_suffix('')
            if sub_path.exists():
                shutil.rmtree(sub_path)

    _JSON_EXT_END = -5

    def list(self, model_class: Type[StoredModel],
             *related_model: Related) -> Iterable[StoredModel]:
        path, lock = self._prepare_file(model_class, '__list__', *related_model)
        with lock:
            for p in os.listdir(path.parent):
                if p.endswith('.json'):
                    yield self.load(model_class, p[:Storage._JSON_EXT_END], *related_model)

    def __str__(self) -> str:
        return f'file.Storage(base_path={self.base_path})'

    def destroy(self) -> None:
        shutil.rmtree(self.base_path)
