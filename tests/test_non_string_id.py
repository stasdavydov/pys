from dataclasses import dataclass
from datetime import datetime

import pytest

import pys


@pys.saveable(field_as_id='date')
@dataclass
class D:
    date: datetime.date


@pytest.fixture
def file_storage():
    s = pys.file_storage('.storage')
    yield s
    s.destroy()


@pytest.fixture
def sqlite_storage():
    s = pys.file_storage('storage.db')
    yield s
    s.destroy()


def test_non_string_id(file_storage, sqlite_storage):
    today = datetime.now().date()
    a = D(date=today)
    assert a.__my_id__() is not None
    assert a.__json__() is not None
    assert a.__json__() == f'{{"date":"{today}"}}'

    def with_storage(s):
        saved_id = s.save(a)
        assert saved_id == a.__my_id__()

        a2 = s.load(D, today)
        assert a.__json__() == a2.__json__()

    with_storage(file_storage)
    with_storage(sqlite_storage)
