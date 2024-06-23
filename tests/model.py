from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel
import pys


class Created(BaseModel):
    created: str = None

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        if self.created is None:
            self.created = datetime.utcnow().isoformat()


class BotBrief(pys.ModelWithID, Created):
    name: str
    enabled: bool = True


class Bot(BotBrief):
    token: Optional[str] = None
    owner_id: Optional[str] = None
    notification_chat_id: Optional[str] = None
    pages: Optional[Any] = None


class User(pys.ModelWithID):
    username: str
    first_name: str
    last_name: str


class BotOwner(User):
    pass


class ResponseContent(BaseModel):
    content: Optional[Any] = None


class BotResponse(pys.ModelWithID, ResponseContent, Created):
    author: User
