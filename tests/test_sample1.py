from dataclasses import dataclass

import pys
from pys.pydantic import ModelWithID


def test_sample_pydantic():
    # Initialize storage with path where files will be saved
    storage = pys.storage('.storage')

    class Author(ModelWithID):
        name: str

    # Persist model Author
    leo = Author(name='Leo Tolstoy')
    storage.save(leo)

    # Load model Author by its ID and check it's the same
    another_leo = storage.load(Author, leo.id)
    assert another_leo.id == leo.id
    assert another_leo.name == leo.name


def test_sample_dataclass():
    # Initialize storage with path where files will be saved
    storage = pys.storage('.storage')

    @pys.saveable
    @dataclass
    class Author:
        name: str

    # Persist model Author
    leo = Author(name='Leo Tolstoy')
    leo_id = storage.save(leo)

    # Load model Author by its ID and check it's the same
    another_leo = storage.load(Author, leo_id)
    assert another_leo.name == leo.name
