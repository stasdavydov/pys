import uuid
from datetime import datetime
from typing import Any, Optional

import pytest
from pydantic import BaseModel

import pys
from pys.pydantic import ModelWithID


class Created(BaseModel):
    created: str = None

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        if self.created is None:
            self.created = datetime.utcnow().isoformat()


class BotBrief(ModelWithID, Created):
    name: str
    enabled: bool = True


class Bot(BotBrief):
    token: Optional[str] = None
    owner_id: Optional[str] = None
    notification_chat_id: Optional[str] = None
    pages: Optional[Any] = None


class User(ModelWithID):
    username: str
    first_name: str
    last_name: str


class BotOwner(User):
    pass


class ResponseContent(BaseModel):
    content: Optional[Any] = None


class BotResponse(ModelWithID, ResponseContent, Created):
    author: User


storages = [
    pys.file_storage('tests.storage'),
    pys.sqlite_storage('tests.db'),
]


@pytest.fixture(params=storages)
def storage(request):
    return request.param


def test_load(storage):
    owner = BotOwner(username='itisme', first_name='Test', last_name='Tester')
    assert owner.id is None
    owner.__my_id__()
    assert str(uuid.UUID(owner.id, version=4))
    storage.save(owner)

    bot_owner = storage.load(BotOwner, owner.id)
    assert bot_owner is not None
    assert bot_owner.id == owner.id
    assert bot_owner.username == owner.username
    assert bot_owner.first_name == owner.first_name
    assert bot_owner.last_name == owner.last_name
    storage.delete(bot_owner.__class__, bot_owner.id)


def test_save(storage):
    bot_owner2a = BotOwner(first_name='Second', last_name='', username='')
    storage.save(bot_owner2a)
    bot_owner2b = storage.load(BotOwner, bot_owner2a.id)
    assert bot_owner2b == bot_owner2a
    storage.delete(BotOwner, bot_owner2a.id)


def test_related_model(storage):
    bot_owner2 = BotOwner(first_name='Second', last_name='Owner', username='')
    bot_owner3 = BotOwner(first_name='Third', last_name='Owner', username='')
    storage.save(Bot(id='3', name='A bot'), bot_owner2)
    storage.save(Bot(id='3', name='B bot'), bot_owner3)

    bot_a = storage.load(Bot, '3', bot_owner2)
    assert bot_a.id == '3'
    assert bot_a.name == 'A bot'

    bot_b = storage.load(Bot, '3', bot_owner3)
    assert bot_b.id == '3'
    assert bot_b.name == 'B bot'

    storage.delete(bot_owner2.__class__, bot_owner2.id)
    storage.delete(bot_owner3.__class__, bot_owner3.id)


def test_related_models(storage):
    bot_owner = BotOwner(first_name='Second', last_name='Owner', username='')
    bot = Bot(id='1', name='A bot')
    storage.save(bot, bot_owner)
    response = BotResponse(author=bot_owner, content='123')
    storage.save(response, bot_owner, bot)

    bot_response = storage.load(BotResponse, response.id, bot_owner, bot)
    assert bot_response.id == response.id
    assert bot_response.content == response.content

    bot_response = storage.load(BotResponse, response.id, bot_owner, (Bot, bot.id))
    assert bot_response.id == response.id
    assert bot_response.content == response.content

    storage.delete(bot_owner.__class__, bot_owner.id)


def test_list(storage):
    bot_owner = BotOwner(first_name='Second', last_name='Owner', username='')
    storage.save(Bot(id='1', name='Bot #1'), bot_owner)
    storage.save(Bot(id='2', name='Bot #2'), bot_owner)
    storage.save(Bot(id='3', name='Bot #3'), bot_owner)

    bot_list = list(storage.list(Bot, bot_owner))
    assert len(bot_list) == 3
    bot_ids = ('1', '2', '3')
    for bot in bot_list:
        assert bot.id in bot_ids

    storage.delete(bot_owner.__class__, bot_owner.id)


def test_tear_down(storage):
    storage.destroy()
