import pytest
from pydantic import BaseModel

import pys
from pys.pydantic import ModelWithID


@pytest.fixture
def storage():
    storage = pys.file_storage('storage.db')
    yield storage
    storage.destroy()


def test_sample_pydantic(storage):
    # An author
    @pys.saveable
    class Author(BaseModel):
        name: str

    # And a book
    @pys.saveable
    class Book(BaseModel):
        title: str

    # A few books of Leo Tolstoy
    leo = Author(name='Leo Tolstoy')
    war_and_peace = Book(title='War and peace')

    # Save Leo's book
    leo_id = storage.save(leo)
    wnp_id = storage.save(war_and_peace, (Author, leo_id))

    # One more author :)
    gpt = Author(name='Chat GPT')
    gpt_id = storage.save(gpt)

    # Do we have the same book by GPT?
    gpt_war_and_peace = storage.load(Book, wnp_id, (Author, gpt_id))
    assert gpt_war_and_peace is None

    # Now it has :)
    wnp_id2 = storage.save(war_and_peace, (Author, gpt_id))
    gpt_war_and_peace = storage.load(Book, wnp_id2, (Author, gpt_id))
    assert gpt_war_and_peace is not None


def test_sample_pydantic_with_model_id(storage):
    # An author
    class Author(ModelWithID):
        name: str

    # And a book
    class Book(ModelWithID):
        title: str

    # A few books of Leo Tolstoy
    leo = Author(name='Leo Tolstoy')
    war_and_peace = Book(title='War and peace')

    # Save Leo's book
    storage.save(leo)
    storage.save(war_and_peace, leo)

    # One more author :)
    gpt = Author(name='Chat GPT')
    storage.save(gpt)

    # Do we have the same book by GPT?
    gpt_war_and_peace = storage.load(Book, war_and_peace.id, gpt)
    assert gpt_war_and_peace is None

    # Now it has :)
    wnp_id2 = storage.save(war_and_peace, gpt)
    gpt_war_and_peace = storage.load(Book, war_and_peace.id, gpt)
    assert gpt_war_and_peace is not None
