from dataclasses import dataclass

import msgspec
import pytest

import pys
from pys.pydantic import ModelWithID


@pytest.fixture
def storage():
    storage = pys.file_storage('storage.db')
    yield storage
    storage.destroy()


def test_sample_pydantic(storage):
    class Author(ModelWithID):
        name: str

    # Persist model Author
    leo = Author(name='Leo Tolstoy')
    storage.save(leo)

    # Load model Author by its ID and check it's the same
    another_leo = storage.load(Author, leo.id)
    assert another_leo.id == leo.id
    assert another_leo.name == leo.name


def test_sample_dataclass(storage):
    @pys.saveable
    @dataclass
    class Author:
        name: str

    # Persist model Author
    leo = Author(name='Leo Tolstoy')
    leo_id = storage.save(leo)
    assert leo_id

    # Load model Author by its ID and check it's the same
    another_leo = storage.load(Author, leo_id)
    assert another_leo.name == leo.name


def test_sample_msgspec(storage):
    @pys.saveable
    class Author(msgspec.Struct):
        id: str
        name: str

    # Persist model Author
    leo = Author(id='leo', name='Leo Tolstoy')
    leo_id = storage.save(leo)

    # Load model Author by its ID and check it's the same
    another_leo = storage.load(Author, leo_id)
    assert another_leo.name == leo.name
