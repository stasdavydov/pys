import abc
import functools
import uuid
from contextlib import contextmanager
from pathlib import Path
from typing import Union, Callable, Any

from . import file, sqlite


def _random_uuid(_) -> str:
    return str(uuid.uuid4())


def _is_dataclass(cls):
    import dataclasses
    return dataclasses.is_dataclass(cls)


def _is_pydantic(cls):
    try:
        from pydantic import BaseModel
        return issubclass(cls, BaseModel)
    except:
        return False


def _is_msgspec_struct(cls):
    try:
        import msgspec
        return issubclass(cls, msgspec.Struct)
    except:
        return False


class Persistent(abc.ABC):
    """
    Base class for any object ready to be persisted
    """
    @classmethod
    def __factory__(cls, raw_content: str, model_id: Any) -> 'Persistent':
        """
        Create object of class from `raw_content` with ID from `model_id`
        :param raw_content: Raw content
        :param model_id: Model ID
        :return: Instance of class
        """
        raise NotImplementedError

    def __json__(self) -> str:
        """
        Get JSON representation of the object
        :return: JSON representation
        """
        raise NotImplementedError


def saveable(base_cls=None, *,
             field_as_id: str = 'id',
             default_id: Callable[[Any], str] = _random_uuid):
    """
    Decorate the given `cls` with `__my_id__()` and `__json__()` methods
    required for persistence.
    :param base_cls: Class to decorate.
    :param field_as_id: existing class field to be used as object ID.
    :param default_id: Default ID value function (id(self) by default).
    :return: Decorated class
    """
    if not base_cls:
        def wrapper(decor_cls):
            return saveable(decor_cls, field_as_id=field_as_id)

        return wrapper

    @functools.wraps(base_cls, updated=())
    class _BasePersistence(base_cls):
        @classmethod
        def __factory__(cls, raw_content: str, model_id: Any) -> base_cls:
            if hasattr(base_cls, '__factory__'):
                return base_cls.__factory__(raw_content, model_id)
            else:
                raise NotImplementedError(
                    f'The class {base_cls} is not msgspec.Struct, @dataclass nor Pydantic Model '
                    f'and does not have __factory__() method. Please implement __factory__() method by yourself.')

        @staticmethod
        def _valid_id(_id: Any) -> Any:
            if not _id:
                raise ValueError('ID shall not be empty')
            return _id

        def _original_id(self) -> Union[Any, None]:
            if hasattr(base_cls, '__my_id__') and callable(cls_my_id := getattr(base_cls, '__my_id__')):
                return cls_my_id(self)
            return None

        def __my_id__(self) -> Any:
            """
            Get object ID to be used for persisting. If `field_as_id` is specified
            then use this field as ID.
            :return: Object's ID
            """
            if original_id := self._original_id():
                return original_id
            _id = getattr(self, field_as_id, None)
            if not _id:
                _id = default_id(self)
                setattr(self, field_as_id, _id)
            return self._valid_id(_id)

        def __json__(self) -> str:
            """
            Get JSON representation of the object
            :return: JSON representation
            """
            if hasattr(base_cls, '__json__'):
                return base_cls.__json__(self)
            else:
                raise NotImplementedError(
                    f'The class {base_cls} is not msgspec.Struct, @dataclass nor Pydantic Model '
                    f'and does not have __json__() method. Please implement __json__() method by yourself.')

    @functools.wraps(base_cls, updated=())
    class _HasMyIdMethod(_BasePersistence):
        def __my_id__(self) -> str:
            return self._original_id()

    @functools.wraps(base_cls, updated=())
    class _NoIdField(_BasePersistence):
        @classmethod
        def _parent_factory(cls) -> Callable[[str, Any], _BasePersistence]:
            raise NotImplementedError

        def set_saved_id(self, model_id: Any):
            self.__my_saved_id__ = model_id

        @classmethod
        def __factory__(cls, raw_content: str, model_id: str) -> '_NoIdField':
            model = cls._parent_factory()(raw_content, model_id)
            model.set_saved_id(model_id)
            return model

        def __my_id__(self) -> str:
            if original_id := self._original_id():
                return original_id
            if not self.__my_saved_id__:
                self.set_saved_id(default_id(self))
            return self._valid_id(self.__my_saved_id__)

    has_id = hasattr(base_cls, field_as_id)
    has_my_id = hasattr(base_cls, '__my_id__') and callable(getattr(base_cls, '__my_id__'))
    parent = _HasMyIdMethod if has_my_id else _BasePersistence

    if _is_pydantic(base_cls):
        has_id = field_as_id in base_cls.__annotations__

        @functools.wraps(base_cls, updated=())
        class _Pydantic(parent):
            @classmethod
            def __factory__(cls, raw_content: str, model_id: Any) -> '_Pydantic':
                return cls.model_validate_json(raw_content)

            def __json__(self) -> str:
                return self.model_dump_json()

        @functools.wraps(base_cls, updated=())
        class _PydanticNoId(_Pydantic, _NoIdField):
            # __slots__ = (MY_SAVED_ID,)
            __my_saved_id__ = None

            @classmethod
            def _parent_factory(cls) -> Callable[[str, Any], _Pydantic]:
                return _Pydantic.factory

        return _Pydantic if has_id or has_my_id else _PydanticNoId

    @functools.wraps(base_cls, updated=())
    class _MsgspecStruct(parent):
        @classmethod
        def __factory__(cls, raw_content: str, model_id: Any) -> '_MsgspecStruct':
            import msgspec
            content = msgspec.json.decode(raw_content)
            return cls(**content)

        def _prepare(self) -> dict:
            return self

        def __json__(self) -> str:
            import msgspec
            return msgspec.json.encode(self._prepare()).decode(encoding='UTF-8')

    @functools.wraps(base_cls, updated=())
    class _MsgspecStructNoIdField(_MsgspecStruct, _NoIdField):
        import msgspec
        __my_saved_id__: Union[str, None, msgspec.UnsetType] = msgspec.UNSET

        @contextmanager
        def without_saved_id(self):
            import msgspec
            copy = self.__my_saved_id__
            try:
                self.__my_saved_id__ = msgspec.UNSET
                yield self
            finally:
                self.__my_saved_id__ = copy

        def __eq__(self, other: '_MsgspecStructNoIdField'):
            if isinstance(other, base_cls):
                with self.without_saved_id(), other.without_saved_id() as _other:
                    return super().__eq__(_other)
            else:
                return super().__eq__(other)

        @classmethod
        def _parent_factory(cls) -> Callable[[str, Any], _MsgspecStruct]:
            return _MsgspecStruct.factory

        def __json__(self) -> str:
            with self.without_saved_id():
                return super().__json__()

    if _is_msgspec_struct(base_cls):
        return _MsgspecStruct if has_id or has_my_id else _MsgspecStructNoIdField

    if _is_dataclass(base_cls):
        has_id = field_as_id in base_cls.__annotations__
        from dataclasses import asdict

        @functools.wraps(base_cls, updated=())
        class _Dataclass(_MsgspecStruct):
            def _prepare(self) -> dict:
                # noinspection PyDataclass
                return asdict(self)

        @functools.wraps(base_cls, updated=())
        class _DataclassNoId(_Dataclass, _NoIdField):
            # __slots__ = ('__my_saved_id__',)
            __my_saved_id__ = None

            @classmethod
            def _parent_factory(cls) -> Callable[[str, Any], _Dataclass]:
                return _Dataclass.factory

        return _Dataclass if has_id or has_my_id else _DataclassNoId

    return _HasMyIdMethod if has_my_id else _BasePersistence


def file_storage(base_path: Union[str, Path]):
    return file.Storage(base_path)


def sqlite_storage(base_path: Union[str, Path]):
    return sqlite.Storage(base_path)


storage = sqlite_storage

__all__ = ('saveable', 'storage', 'file_storage', 'sqlite_storage', 'Persistent')
