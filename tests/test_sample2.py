import pys


def test_sample():
    # An author
    class Author(pys.ModelWithID):
        name: str

    # And a book
    class Book(pys.ModelWithID):
        title: str

    storage = pys.storage('.storage')

    # A few books of Leo Tolstoy
    leo = Author(name='Leo Tolstoy')
    war_and_peace = Book(title='War and peace')

    # Save Leo's book
    storage.save(leo)
    storage.save(war_and_peace, leo)

    # One more author :)
    gpt = Author(name='Chat GPT')

    # Do we have the same book by GPT?
    gpt_war_and_peace = storage.load(Book, war_and_peace.id, gpt)
    assert gpt_war_and_peace is None

    # Now it has :)
    storage.save(war_and_peace, gpt)
    gpt_war_and_peace = storage.load(Book, war_and_peace.id, gpt)
    assert gpt_war_and_peace is not None
