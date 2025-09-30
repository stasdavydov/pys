import os
from pathlib import Path
from typing import Type, Any, Optional, Iterable, Union

import zipremove as zipfile

from pys import file
from pys.base import StoredModel, Related


class Storage(file.Storage):
    def __init__(self, base_path: Union[str, Path]) -> None:
        """
        Base path for the storage file
        :param base_path: base path.
        """
        super().__init__(base_path)

    def load(self, model_class: Type[StoredModel], model_id: Any, *related_model: Related) -> Optional[StoredModel]:
        with zipfile.ZipFile(self.base_path, 'r') as root:
            path = self._get_model_path(
                model_class, model_id, *related_model).with_suffix('.json').as_posix()
            return model_class.__factory__(root.read(path), model_id)

    def save(self, model: StoredModel, *related_model: Related) -> Any:
        with zipfile.ZipFile(self.base_path, 'a', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as root:
            path = self._get_model_path(
                model.__class__, model.__my_id__(), *related_model).with_suffix('.json').as_posix()
            root.writestr(str(path), model.__json__())

    def delete(self, model_class: Type[StoredModel], model_id: Any, *related_model: Related) -> None:
        with zipfile.ZipFile(self.base_path, 'a') as root:
            path = self._get_model_path(model_class, model_id, *related_model).with_suffix('.json').as_posix()
            try:
                root.remove(path)
            except KeyError:
                pass

    def list(self, model_class: Type[StoredModel], *related_model: Related) -> Iterable[StoredModel]:
        with zipfile.ZipFile(self.base_path, 'r') as root:
            path = zipfile.Path(
                root,
                f"{self._get_model_path(model_class, '__list__', *related_model).parent.as_posix()}/",
            )
            for mf in path.iterdir():
                if mf.name.endswith(".json"):
                    yield self.load(model_class, mf.name[:Storage._JSON_EXT_END], *related_model)

    def destroy(self) -> None:
        os.unlink(self.base_path)
