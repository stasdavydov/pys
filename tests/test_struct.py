import msgspec
import pytest

import pys


@pys.saveable(field_as_id='some_other')
class A(msgspec.Struct):
    some_other: str


@pys.saveable
class B(msgspec.Struct):
    id: str


@pys.saveable
class C(msgspec.Struct):
    name: str


def test_with_id():
    a = A(some_other='xyz')
    assert a.__my_id__() is not None
    assert a.some_other is not None
    assert a.some_other == a.__my_id__()
    assert a.__json__() is not None
    assert a.__json__() == '{"some_other":"' f'{a.__my_id__()}' '"}'

    b = B(id='123')
    assert b.__my_id__() is not None
    assert b.id == b.__my_id__()
    assert b.id == '123'
    assert b.__json__() is not None
    assert b.__json__() == '{"id":"' f'{b.id}' '"}'

    c = C(name='C class')
    assert c.__my_id__() is not None
    assert c.__json__() is not None
    assert c.__json__() == f'{{"name":"{c.name}"}}'


@pys.saveable
class D(msgspec.Struct):
    a: A
    b: B
    c: C


@pytest.fixture
def storage():
    storage = pys.file_storage('storage.db')
    yield storage
    storage.destroy()


@pytest.mark.skip("We didn't support embedded for msgspec yet")
def test_embedded(storage):
    d = D(a=A(some_other='123'), b=B(id='456'), c=C(name='789'))
    d_id = storage.save(d)
    d_copy = storage.load(D, model_id=d_id)

    assert d == d_copy
