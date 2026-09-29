from dataclasses import dataclass

import pytest

import pys
from test_with_id import A, B, C


@pys.saveable
@dataclass
class D:
    a: A
    b: B
    c: C


@pytest.fixture
def storage():
    storage = pys.file_storage('storage.db')
    yield storage
    storage.destroy()


def test_embedded(storage):
    d = D(a=A(some_other='123'), b=B(id='456'), c=C(name='789'))
    d_id = storage.save(d)
    d_copy = storage.load(D, model_id=d_id)

    assert d == d_copy
