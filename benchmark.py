import time

import msgspec
from google.auth.credentials import AnonymousCredentials
from testcontainers.core.container import DockerContainer
from google.cloud import storage as gcs_storage
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

with (
        DockerContainer("fsouza/fake-gcs-server")
                .with_command("-scheme http -port 4443 -backend memory")
                .with_exposed_ports(4443)
) as container:
    host = container.get_container_host_ip()
    port = container.get_exposed_port(4443)
    endpoint = f"http://{host}:{port}"

    gcs_client = gcs_storage.Client(
        project="test-project",
        credentials=AnonymousCredentials(),
        client_options={"api_endpoint": endpoint},
    )

    gcs_client.create_bucket("test-bucket")

    storages = (
        pys.file_storage('benchmark.storage'),
        pys.sqlite_storage('benchmark.db'),
        pys.zip_storage('benchmark.zip'),
        pys.in_memory_storage(),
        pys.gcs_storage(
            bucket="test-bucket",
            prefix=f"tests/benchmark/",
            client=gcs_client,
        )
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
        total1 = AUTHORS + AUTHORS * BOOKS * 2

        start = time.time_ns()
        authors_found = list(s.list(Author))
        assert AUTHORS == len(authors_found), f"Wrong number of authors: {len(authors_found)}, expected: {AUTHORS}"
        end = time.time_ns()
        t2 = end - start
        total2 = AUTHORS

        start = time.time_ns()
        for author in authors_found:
            books = list(s.list(Book, author))
            assert len(books) == BOOKS
        end = time.time_ns()
        t3 = end - start
        total3 = len(authors_found) * BOOKS

        start = time.time_ns()
        books = list(s.list(Book))
        assert len(books) == BOOKS*AUTHORS
        end = time.time_ns()
        t4 = end - start
        total4 = len(books)

        NS_IN_MS = 1_000_000

        print(f'Storage: {s}')
        print(f'T1: {t1/NS_IN_MS:.2f} ms -- save {total1} objects -- {t1/NS_IN_MS/total1:.3f} ms per object')
        print(f'T2: {t3/NS_IN_MS:.2f} ms -- list {total3} objects -- {t3/NS_IN_MS/total3:.3f} ms per object')
        print(f'T3: {t4/NS_IN_MS:.2f} ms -- list {total4} objects -- {t4/NS_IN_MS/total4:.3f} ms per object')

        s.destroy()

    gcs_client.close()
