import pys


# An author
class Author(pys.ModelWithID):
    name: str


# And a book
class Book(pys.ModelWithID):
    title: str


def test_sample():
    storage = pys.storage('.storage')

    # A few books of Leo Tolstoy
    leo = Author(name='Leo Tolstoy')
    war_and_peace = Book(title='War and peace')
    for_kids = Book(title='For Kids')

    storage.save(leo)
    storage.save(war_and_peace, leo)
    storage.save(for_kids, leo)

    leo_books = list(storage.list(Book, leo))
    assert len(leo_books) == 2
    assert war_and_peace in leo_books
    assert for_kids in leo_books
