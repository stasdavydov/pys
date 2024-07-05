import uuid
from dataclasses import is_dataclass, asdict
from pathlib import Path
from typing import Union

import msgspec

from .base import is_pydantic
from . import file, sqlite


def saveable(cls=None, /, field_as_id: str = 'id'):
    def wrapper(cls):
        def my_id_or_default(self):
            if hasattr(self, field_as_id):
                if getattr(self, field_as_id, None) is None:
                    setattr(self, field_as_id, str(uuid.uuid4()))
                return getattr(self, field_as_id)
            else:
                return str(id(self))

        setattr(cls, '__my_id__', my_id_or_default)
        if not hasattr(cls, '__json__'):
            if issubclass(cls, msgspec.Struct):
                setattr(cls, '__json__',
                        lambda self:
                            msgspec.json.encode(self).decode(encoding='UTF-8')
                        )
            elif is_dataclass(cls):
                setattr(cls, '__json__',
                        lambda self:
                            msgspec.json.encode(
                                asdict(self),
                            ).decode(encoding='UTF-8')
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


def file_storage(base_path: Union[str, Path]):
    return file.Storage(base_path)


def sqlite_storage(base_path: Union[str, Path]):
    return sqlite.Storage(base_path)


storage = sqlite_storage

__all__ = ('saveable', 'storage', 'file_storage', 'sqlite_storage')
