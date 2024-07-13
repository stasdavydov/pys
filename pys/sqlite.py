import os
import re
import sqlite3
from pathlib import Path
from typing import Type, Iterable, Optional, Any

from .base import BaseStorage, StoredModel, Related


class Storage(BaseStorage):
    con = None

    def _ensure_table_exist(self, table_name):
        for cnt in self.con.execute(
                "select count(name) from sqlite_master where type='table' and name=?;",
                (table_name,)
        ):
            if not cnt[0] == 1:
                self.con.execute(
                    f"""
                    create table {table_name} (
                        id varchar(255) not null,
                        data json,
                        related_id varchar(255),
                        related_name varchar(255),
                        unique (id, related_id, related_name)
                    );

                    """
                )

    @staticmethod
    def _get_table_name(cls):
        return re.sub(r'\W', '_', cls.__name__).lower()

    def __init__(self, path: Path):
        self.base_path = Path(path)
        self.con = sqlite3.connect(self.base_path)

    @staticmethod
    def _related(related_model: Related):
        (prev_cls, prev_id) = None, None
        if related_model:
            if isinstance(related_model, tuple):
                (prev_cls, prev_id) = related_model
            else:
                (prev_cls, prev_id) = related_model.__class__, related_model.__my_id__()
        return prev_cls, prev_id

    def load(self, model_class: Type[StoredModel], model_id: str, *related_model: Related) -> Optional[StoredModel]:
        last_related = related_model[-1] if related_model else None
        (rel_cls, rel_id) = self._related(last_related)

        table_name = self._get_table_name(model_class)
        self._ensure_table_exist(table_name)

        for row in self.con.execute(
            f"""
            select id, data, related_id, related_name
            from {table_name}
            where 
                id=? and {'related_id=? and related_name=?' if rel_id else 'related_id is null'}
            """,
            (model_id, rel_id, rel_cls.__name__) if last_related else (model_id,),
        ):
            return model_class.__factory__(row[1], row[0])
        else:
            return None

    def _save(self, model: StoredModel, prev=Related):
        table_name = self._get_table_name(model.__class__)
        self._ensure_table_exist(table_name)

        (prev_cls, prev_id) = self._related(prev)
        self.con.execute(
            f"""
            insert into {table_name} (id, data, related_id, related_name)
            values (?, ?, ?, ?) 
            on conflict do update set data=excluded.data;
            """,
            (model.__my_id__(),
             model.__json__(),
             prev_id,
             prev_cls.__name__ if prev else None,),
        )
        return model.__my_id__()

    def save(self, model: StoredModel, *related_model: Related) -> Any:
        prev_model = None
        last_id = None
        for m in related_model + (model,):
            last_id = self._save(m, prev=prev_model)
            prev_model = m
        return last_id

    def delete(self, model_class: Type[StoredModel], model_id: str, *related_model: Related) -> None:
        last_related = related_model[-1] if related_model else None
        (prev_cls, prev_id) = self._related(last_related)

        table_name = self._get_table_name(model_class)
        self._ensure_table_exist(table_name)

        self.con.execute(
            f"""
            delete from {table_name}
            where id=? and related_id=? and related_name=? 
            """,
            (model_id, prev_id, prev_cls.__name__ if prev_cls else None,)
        )

    def list(self, model_class: Type[StoredModel], *related_model: Related) -> Iterable[StoredModel]:
        last_related = related_model[-1] if related_model else None
        (prev_cls, prev_id) = self._related(last_related)

        table_name = self._get_table_name(model_class)
        self._ensure_table_exist(table_name)

        return [model_class.__factory__(row[1], row[0]) for row in self.con.execute(
            f"""
            select distinct id, data, related_id, related_name
            from {table_name}
            where {'related_id=? and related_name=?' if prev_cls else 'related_id is null'}   
            """,
            (prev_id, prev_cls.__name__) if prev_cls else (),
        )]

    def destroy(self) -> None:
        self.con.close()
        if self.base_path.exists():
            os.unlink(self.base_path)

    def __str__(self) -> str:
        return f'sqlite.Storage(base_path={self.base_path})'
