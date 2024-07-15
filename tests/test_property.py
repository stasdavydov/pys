import re
from dataclasses import dataclass

import msgspec
from pydantic import BaseModel

import pys


def test_dataclass():
    @dataclass
    class Url:
        url: str

        @staticmethod
        def to_id(url: str) -> str:
            NON_ALNUM = re.compile(r'([^a-zA-Z0-9_]+)')
            return NON_ALNUM.sub('_', url)

        def __my_id__(self):
            return Url.to_id(self.url)

    @pys.saveable
    @dataclass
    class Link(Url):
        a: int = 0

    link = Link('https://example.com/')
    assert link.__my_id__() == Url.to_id(link.url)


def test_msgspec():
    class Url(msgspec.Struct):
        url: str

        @staticmethod
        def to_id(url: str) -> str:
            NON_ALNUM = re.compile(r'([^a-zA-Z0-9_]+)')
            return NON_ALNUM.sub('_', url)

        def __my_id__(self):
            return Url.to_id(self.url)

    @pys.saveable
    class Link(Url):
        a: int = 0

    link = Link('https://example.com/')
    assert link.__my_id__() == Url.to_id(link.url)


def test_pydantic():
    class Url(BaseModel):
        url: str

        @staticmethod
        def to_id(url: str) -> str:
            NON_ALNUM = re.compile(r'([^a-zA-Z0-9_]+)')
            return NON_ALNUM.sub('_', url)

        def __my_id__(self):
            return Url.to_id(self.url)

    @pys.saveable
    class Link(Url):
        a: int = 0

    link = Link(url='https://example.com/')
    assert link.__my_id__() == Url.to_id(link.url)
