from dataclasses import dataclass

import pys


@pys.saveable(field_as_id='some_other')
@dataclass
class A:
    some_other: str


@pys.saveable
@dataclass
class B:
    id: str


@pys.saveable
@dataclass
class C:
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
