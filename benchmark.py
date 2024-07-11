import time

import msgspec

import pys


@pys.saveable(field_as_id='id')
class Author(msgspec.Struct):
    id: str
    name: str


@pys.saveable(field_as_id='id')
class Book(msgspec.Struct):
    id: str
    author_id: str
    title: str


AUTHORS = 100
BOOKS = 5

storages = (
    pys.file_storage('benchmark.storage'),
    pys.sqlite_storage('benchmark.db'),
)
for s in storages:
    start = time.time_ns()
    for i in range(0, AUTHORS):
        author = Author(id=str(i), name=f'Author {i}')
        s.save(author)
        for j in range(0, BOOKS):
            book = Book(id=str(i*AUTHORS + j), title=f'Book {i}-{j}', author_id=author.__my_id__())
            s.save(book, author)
            s.save(book)
    end = time.time_ns()
    t1 = end - start

    start = time.time_ns()
    authors_found = list(s.list(Author))
    assert AUTHORS == len(authors_found)
    end = time.time_ns()
    t2 = end - start

    start = time.time_ns()
    for author in authors_found:
        books = list(s.list(Book, author))
        assert len(books) == BOOKS
    end = time.time_ns()
    t3 = end - start

    start = time.time_ns()
    books = list(s.list(Book))
    assert len(books) == BOOKS*AUTHORS
    end = time.time_ns()
    t4 = end - start

    print(f'Storage: {s}')
    print(f'T1: {t1/1000000:.2f} ms')
    print(f'T2: {t2/1000000:.2f} ms')
    print(f'T3: {t3/1000000:.2f} ms')
    print(f'T4: {t4/1000000:.2f} ms')

    s.destroy()

# path.glob
# T1: 1.28 sec
# T2: 0.35 sec
# T3: 2.21 sec
# T4: 2.01 sec
#
# os.listdir
# T1: 0.68 sec
# T2: 0.24 sec
# T3: 1.44 sec
# T4: 1.25 sec

# msgspec
# T1: 0.62 sec
# T2: 0.24 sec
# T3: 1.44 sec
# T4: 1.25 sec

# SQLite storage is added
# T1: 656.80 ms
# T2: 264.35 ms
# T3: 1368.96 ms
# T4: 1182.48 ms
# Storage: sqlite.Storage(base_path=benchmark.db)
# T1: 20.00 ms
# T2: 1.00 ms
# T3: 6.51 ms
# T4: 1.00 ms
