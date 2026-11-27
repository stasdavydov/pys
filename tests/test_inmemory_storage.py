from dataclasses import dataclass

import pys


def test():
    s1 = pys.in_memory_storage()

    @pys.saveable
    @dataclass
    class A:
        b: str

    a = A("xyz")
    a_id = s1.save(a)

    s2 = pys.in_memory_storage()
    a_copy = s2.load(A, a_id)

    assert a_copy
    assert a_copy.b == a.b

    s2.destroy()


def test_auto_saving_off():
    s1 = pys.in_memory_storage(auto_saving=False)

    @pys.saveable
    @dataclass
    class A:
        b: str

    a1 = A("xyz")
    a2 = A("abc")
    a3 = A("klm")

    a1_id = s1.save(a1)
    a2_id = s1.save(a2)
    a3_id = s1.save(a3)

    s2 = pys.in_memory_storage(auto_saving=False)
    assert s2.load(A, a1_id) is None
    assert s2.load(A, a2_id) is None
    assert s2.load(A, a3_id) is None

    s1.persist()
    s2 = pys.in_memory_storage(auto_saving=False)
    assert s2.load(A, a1_id) is not None
    assert s2.load(A, a2_id) is not None
    assert s2.load(A, a3_id) is not None

    s1.delete(A, a2_id)
    s2 = pys.in_memory_storage(auto_saving=False)
    assert s2.load(A, a1_id) is not None
    assert s2.load(A, a2_id) is not None
    assert s2.load(A, a3_id) is not None

    s1.persist()
    s2 = pys.in_memory_storage(auto_saving=False)
    assert s2.load(A, a1_id) is not None
    assert s2.load(A, a2_id) is None
    assert s2.load(A, a3_id) is not None
