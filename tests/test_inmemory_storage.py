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
