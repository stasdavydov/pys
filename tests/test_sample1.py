import pys


def test_sample():
    # Initialize storage with path where files will be saved
    storage = pys.storage('.storage')

    class Author(pys.ModelWithID):
        name: str

    # Persist model Author
    leo = Author(name='Leo Tolstoy')
    storage.save(leo)

    # Load model Author by its ID and check it's the same
    another_leo = storage.load(Author, leo.id)
    assert another_leo.id == leo.id
    assert another_leo.name == leo.name
