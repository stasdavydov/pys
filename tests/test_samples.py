from dataclasses import dataclass
from typing import Any

import msgspec
import pytest
from pydantic import BaseModel
from pys.pydantic import ModelWithID

import pys


@pytest.fixture
def storage():
    storage = pys.file_storage('storage.db')
    yield storage
    storage.destroy()


def dataclass_cases() -> list[tuple]:
    @pys.saveable
    @dataclass
    class AuthorDcNoId:
        name: str

    @pys.saveable
    @dataclass
    class BookDcNoId:
        title: str

    @pys.saveable
    @dataclass
    class AuthorDcWithId:
        name: str
        id: str = None

    @pys.saveable
    @dataclass
    class BookDcWithId:
        title: str
        id: str = None

    @pys.saveable(field_as_id='name')
    @dataclass
    class AuthorDcWithCustomId:
        name: str

    @pys.saveable(field_as_id='title')
    @dataclass
    class BookDcWithCustomId:
        title: str

    return [
        (AuthorDcNoId, BookDcNoId),
        (AuthorDcWithId, BookDcWithId),
        (AuthorDcWithCustomId, BookDcWithCustomId),
    ]


def msgspec_structs() -> list[tuple]:
    @pys.saveable
    class AuthorStructNoId(msgspec.Struct):
        name: str

    @pys.saveable
    class BookStructNoId(msgspec.Struct):
        title: str

    @pys.saveable
    class AuthorStructWithId(msgspec.Struct):
        name: str
        id: str = None

    @pys.saveable
    class BookStructWithId(msgspec.Struct):
        title: str
        id: str = None

    @pys.saveable(field_as_id='name')
    class AuthorStructWithCustomId(msgspec.Struct):
        name: str

    @pys.saveable(field_as_id='title')
    class BookStructWithCustomId(msgspec.Struct):
        title: str

    return [
        (AuthorStructNoId, BookStructNoId),
        (AuthorStructWithId, BookStructWithId),
        (AuthorStructWithCustomId, BookStructWithCustomId),
    ]


def pydantic_models() -> list[tuple]:
    @pys.saveable
    class AuthorPdNoId(BaseModel):
        name: str

    @pys.saveable
    class BookPdNoId(BaseModel):
        title: str

    @pys.saveable
    class AuthorPdWithId(BaseModel):
        name: str
        id: str = None

    @pys.saveable
    class BookPdWithId(BaseModel):
        title: str
        id: str = None

    @pys.saveable(field_as_id='name')
    class AuthorPdWithCustomId(BaseModel):
        name: str

    @pys.saveable(field_as_id='title')
    class BookPdWithCustomId(BaseModel):
        title: str

    return [
        (AuthorPdNoId, BookPdNoId),
        (AuthorPdWithId, BookPdWithId),
        (AuthorPdWithCustomId, BookPdWithCustomId),
    ]


def models_with_id() -> list[tuple]:
    class AuthorModelWithId(ModelWithID):
        name: str

    class BookModelWithId(ModelWithID):
        title: str

    return [
        (AuthorModelWithId, BookModelWithId),
    ]


def custom_cases() -> list[tuple]:
    @pys.saveable(field_as_id='name')
    class CustomAuthor(pys.Persistent):
        name: str

        def __init__(self, name):
            self.name = name

        @classmethod
        def __factory__(cls, raw_content: str, model_id: Any) -> 'CustomAuthor':
            return CustomAuthor(raw_content)

        def __json__(self) -> str:
            return self.name

        def __eq__(self, o: object) -> bool:
            return self.name == o.name

    @pys.saveable(field_as_id='title')
    class CustomBook(pys.Persistent):
        title: str

        def __init__(self, title):
            self.title = title

        @classmethod
        def __factory__(cls, raw_content: str, model_id: Any) -> 'CustomBook':
            return CustomBook(raw_content)

        def __json__(self) -> str:
            return self.title

        def __eq__(self, o: object) -> bool:
            return self.title == o.title

    return [
        (CustomAuthor, CustomBook),
    ]


@pytest.mark.parametrize(
    argnames=('cls_author', 'cls_book'),
    argvalues=dataclass_cases() + msgspec_structs() + pydantic_models() + models_with_id() + custom_cases()
)
def test_sample(storage, cls_author, cls_book):
    leo = cls_author(name='Leo Tolstoy')
    storage.save(leo)
    assert leo.__my_id__()

    leo2 = storage.load(cls_author, leo.__my_id__())
    assert leo2.name == leo.name

    war_and_peace = cls_book(title='War and peace')
    storage.save(war_and_peace, leo)
    gpt = cls_author(name='Chat GPT')
    storage.save(gpt)
    gpt_war_and_peace = storage.load(cls_book, war_and_peace.__my_id__(), gpt)
    assert gpt_war_and_peace is None

    storage.save(war_and_peace, gpt)
    gpt_war_and_peace = storage.load(cls_book, war_and_peace.__my_id__(), gpt)
    assert gpt_war_and_peace is not None

    for_kids = cls_book(title='For Kids')
    storage.save(for_kids, leo)
    leo_books = list(storage.list(cls_book, leo))
    assert len(leo_books) == 2
    assert war_and_peace in leo_books
    assert for_kids in leo_books
