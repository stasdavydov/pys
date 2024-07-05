import shutil
import time
from dataclasses import dataclass

import pys


@pys.saveable(field_as_id='name')
@dataclass
class Author:
    name: str


@pys.saveable(field_as_id='title')
@dataclass
class Book:
    author_id: str
    title: str


AUTHORS = 100
BOOKS = 5

STORAGE = '.benchmark'
s = pys.storage(STORAGE)

start = time.time()
for i in range(0, AUTHORS):
    author = Author(name=f'Author {i}')
    s.save(author)
    for j in range(0, BOOKS):
        book = Book(title=f'Book {i}-{j}', author_id=author.__my_id__())
        s.save(book, author)
        s.save(book)
end = time.time()
t1 = end - start


start = time.time()
authors_found = list(s.list(Author))
assert AUTHORS == len(authors_found)
end = time.time()
t2 = end - start

start = time.time()
for author in authors_found:
    books = list(s.list(Book, author))
    assert len(books) == BOOKS
end = time.time()
t3 = end - start

start = time.time()
books = list(s.list(Book))
assert len(books) == BOOKS*AUTHORS
end = time.time()
t4 = end - start


print(f'T1: {t1:.2f} sec')
print(f'T2: {t2:.2f} sec')
print(f'T3: {t3:.2f} sec')
print(f'T4: {t4:.2f} sec')

shutil.rmtree(STORAGE)

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
