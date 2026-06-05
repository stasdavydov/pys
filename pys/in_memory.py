import json
import pathlib
import re
from typing import Type, Iterable, Any, Optional

from pys.base import BaseStorage, StoredModel, Related


class Storage(BaseStorage):
    class Mem(dict):
        @staticmethod
        def __my_id__():
            return 'mem'

        @classmethod
        def __factory__(cls, raw_content: str, model_id: Any):
            import msgspec
            content = msgspec.json.decode(raw_content)
            return cls(**content)

        def __json__(self):
            return json.dumps(self)

    mem: Mem

    def _init_mem(self, reset_mem: bool = False):
        if not reset_mem:
            self.mem = self.parent.load(self.Mem, self.Mem.__my_id__())
        if not self.mem:
            self.mem = self.Mem()

    def __init__(self, parent: BaseStorage) -> None:
        self.parent = parent
        self._init_mem()

    @staticmethod
    def _get_model_path(model_class: Type[StoredModel], model_id: Any, *related_model: Related) -> str:
        path = pathlib.PurePosixPath()
        if not related_model:
            path /= ''
        else:
            for model in related_model:
                if isinstance(model, tuple):
                    path /= Storage._get_model_path(*model)
                else:
                    path /= Storage._get_model_path(model.__class__, model.__my_id__())

        return str(path / model_class.__name__ / str(model_id))

    def load(self, model_class: Type[StoredModel], model_id: Any, *related_model: Related) -> Optional[StoredModel]:
        key = self._get_model_path(model_class, model_id, *related_model)
        if key in self.mem:
            return model_class.__factory__(self.mem[key], model_id)
        else:
            return None

    def save(self, model: StoredModel, *related_model: Related) -> Any:
        model_id = model.__my_id__()
        key = self._get_model_path(model.__class__, model_id, *related_model)
        self.mem[key] = model.__json__()

        self.parent.save(self.mem)

        return model_id

    def delete(self, model_class: Type[StoredModel], model_id: Any, *related_model: Related) -> None:
        key = self._get_model_path(model_class, model_id, *related_model)

        for k in [k for k in self.mem.keys() if k.startswith(key)]:
            del self.mem[k]

        self.parent.save(self.mem)

    def list(self, model_class: Type[StoredModel], *related_model: Related) -> Iterable[StoredModel]:
        key = self._get_model_path(model_class, "", *related_model)
        path_key = f"{key}/"
        key_exp = re.compile(fr'^{key}/[^/]+$')
        for k in filter(lambda k: key_exp.match(k), self.mem.keys()):
            yield self.load(model_class, k[len(path_key):], *related_model)

    def destroy(self) -> None:
        self._init_mem(reset_mem=True)
        self.parent.destroy()

    def __str__(self) -> str:
        return f'in_memory.Storage(parent={self.parent})'
