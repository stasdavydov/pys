import shutil
from pathlib import Path


from .model import BotOwner, Bot, BotResponse
import pys

base_path = Path(__file__).parent / '.storage'
shutil.rmtree(base_path, ignore_errors=True)
base_path.mkdir(parents=True, exist_ok=False)
storage = pys.storage(base_path)


def test_file_storage():
    bot_owner = BotOwner(username='itisme', first_name='Test', last_name='Tester')
    assert storage.base_path.absolute() == base_path.absolute()
    path, _ = storage._prepare_file(BotOwner, bot_owner.id)
    assert path.absolute() == (base_path / 'BotOwner' / bot_owner.id).with_suffix('.json').absolute()
    storage.delete(bot_owner.__class__, bot_owner.id)


def test_load():
    owner = BotOwner(username='itisme', first_name='Test', last_name='Tester')
    storage.save(owner)
    bot_owner = storage.load(BotOwner, owner.id)
    assert bot_owner is not None
    assert bot_owner.id == owner.id
    assert bot_owner.username == owner.username
    assert bot_owner.first_name == owner.first_name
    assert bot_owner.last_name == owner.last_name
    storage.delete(bot_owner.__class__, bot_owner.id)


def test_save():
    bot_owner2a = BotOwner(first_name='Second', last_name='', username='')
    storage.save(bot_owner2a)
    assert (storage.base_path / 'BotOwner' / bot_owner2a.id).with_suffix('.json').exists()
    bot_owner2b = storage.load(BotOwner, bot_owner2a.id)
    assert bot_owner2b == bot_owner2a

    storage.delete(BotOwner, bot_owner2a.id)
    assert not (storage.base_path / 'BotOwner' / bot_owner2a.id).with_suffix('.json').exists()


def test_related_model():
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


def test_related_models():
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


def test_list():
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
