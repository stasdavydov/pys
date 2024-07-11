import pytest
from pydantic import BaseModel

import pys


@pytest.fixture
def storage():
    storage = pys.storage('storage.db')
    yield storage
    storage.destroy()


def test_sample_pydantic2(storage):
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
    storage.save(leo)
    wnp_id = storage.save(war_and_peace, leo)

    # One more author :)
    gpt = Author(name='Chat GPT')

    # Do we have the same book by GPT?
    gpt_war_and_peace = storage.load(Book, wnp_id, gpt)
    assert gpt_war_and_peace is None

    # Now it has :)
    storage.save(war_and_peace, gpt)
    gpt_war_and_peace = storage.load(Book, wnp_id, gpt)
    assert gpt_war_and_peace is not None
