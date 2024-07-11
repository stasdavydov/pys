import functools
from dataclasses import is_dataclass, asdict
from pathlib import Path
from typing import Union, Callable, Any

import msgspec

from .base import is_pydantic
from . import file, sqlite


def saveable(cls=None, *,
             field_as_id: str = 'id',
             default_id: Callable[[Any], str] = lambda self: str(id(self))):
    """
    Decorate the given `cls` with `__my_id__()` and `__json__()` methods
    required for persistence.
    :param cls: Class to decorate.
    :param field_as_id: existing class field to be used as object ID.
    :param default_id: Default ID value function (id(self) by default).
    :return: Decorated class
    """
    if cls:
        @functools.wraps(cls, updated=())
        class _Persisted(cls):
            def __my_id__(self):
                """
                Get object ID to be used for persisting. If `field_as_id` is specified
                then use this field as ID, otherwise use `id()`
                :return: Object's ID
                """
                if field_as_id and hasattr(self, field_as_id):
                    if not getattr(self, field_as_id, None):
                        setattr(self, field_as_id, default_id(self))
                    _id = getattr(self, field_as_id)
                else:
                    _id = default_id(self)
                if not _id:
                    raise ValueError('ID shall not be empty')
                return _id

            def __json__(self):
                """
                Get JSON representation of the object
                :return: JSON representation
                """
                if issubclass(cls, msgspec.Struct):
                    return msgspec.json.encode(self).decode(encoding='UTF-8')
                elif is_dataclass(cls):
                    return msgspec.json.encode(asdict(self)).decode(encoding='UTF-8')
                elif is_pydantic(cls):
                    return self.model_dump_json()
                elif hasattr(cls, '__json__'):
                    return cls.__json__(self)
                else:
                    raise NotImplementedError(
                        f'The class {cls} is not msgspec.Struct, @dataclass nor Pydantic Model '
                        f'and does not have __json__() method. Please implement __json__() method by yourself.')

        return _Persisted
    else:
        def wrapper(decor_cls):
            return saveable(decor_cls, field_as_id=field_as_id)
        return wrapper


def file_storage(base_path: Union[str, Path]):
    return file.Storage(base_path)


def sqlite_storage(base_path: Union[str, Path]):
    return sqlite.Storage(base_path)


storage = sqlite_storage

__all__ = ('saveable', 'storage', 'file_storage', 'sqlite_storage')
