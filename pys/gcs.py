from typing import Any, Iterable, Optional, Type, Union
from urllib.parse import quote, unquote

from google.api_core.exceptions import NotFound
from google.cloud import storage

from pys.base import StoredModel, Related, BaseStorage


class Storage(BaseStorage):
    """
    Google Cloud Storage backend for pysdato.

    Each model is stored as a separate JSON object.
    Supports hierarchical relations between models.
    """

    def __init__(
        self,
        bucket: str,
        prefix: str,
        client: Union[storage.Client, None] = None,
    ) -> None:
        self.client = client or storage.Client()
        self.bucket = self.client.bucket(bucket)
        self.prefix = prefix.strip("/")
        if self.prefix:
            self.prefix += "/"

    @staticmethod
    def _model_path(
        model_class: Type[StoredModel],
        model_id: Any,
        *related_model: Related,
    ) -> str:
        parts = []

        for model in related_model:
            if isinstance(model, tuple):
                cls, obj_id = model
            else:
                cls = type(model)
                obj_id = model.__my_id__()

            parts.extend((
                cls.__name__,
                quote(str(obj_id), safe=""),
            ))

        parts.extend((
            model_class.__name__,
            quote(str(model_id), safe=""),
        ))

        return "/".join(parts)

    def _key(
        self,
        model_class: Type[StoredModel],
        model_id: Any,
        *related_model: Related,
    ) -> str:
        path = self._model_path(
            model_class, model_id, *related_model
        )
        return f"{self.prefix}{path}.json"

    def save(
        self,
        model: StoredModel,
        *related_model: Related,
    ) -> Any:
        model_id = model.__my_id__()
        key = self._key(
            type(model), model_id, *related_model
        )

        self.bucket.blob(key).upload_from_string(
            model.__json__(),
            content_type="application/json",
        )

        return model_id

    def load(
        self,
        model_class: Type[StoredModel],
        model_id: Any,
        *related_model: Related,
    ) -> Optional[StoredModel]:
        key = self._key(
            model_class, model_id, *related_model
        )

        try:
            data = self.bucket.blob(key).download_as_text(
                encoding="utf-8"
            )
        except NotFound:
            return None

        return model_class.__factory__(data, model_id)

    def delete(
        self,
        model_class: Type[StoredModel],
        model_id: Any,
        *related_model: Related,
    ) -> None:
        key = self._key(
            model_class, model_id, *related_model
        )

        # Delete the model itself.
        try:
            self.bucket.blob(key).delete()
        except NotFound:
            pass

        # Delete all dependent models recursively.
        children_prefix = key[:-5] + "/"

        for blob in self.client.list_blobs(
            self.bucket, prefix=children_prefix
        ):
            try:
                blob.delete()
            except NotFound:
                pass

    def list(
        self,
        model_class: Type[StoredModel],
        *related_model: Related,
    ) -> Iterable[StoredModel]:
        directory = self._model_path(
            model_class, "",
            *related_model,
        ).rsplit("/", 1)[0]

        prefix = f"{self.prefix}{directory}/"

        for blob in self.client.list_blobs(
            self.bucket, prefix=prefix, delimiter="/"
        ):
            filename = blob.name[len(prefix):]

            if not filename.endswith(".json"):
                continue

            model_id = unquote(filename[:-5])

            # Use the model's own deserializer.
            data = blob.download_as_text(encoding="utf-8")
            yield model_class.__factory__(
                data, model_id
            )

    def destroy(self) -> None:
        if not self.prefix:
            raise ValueError(
                "Refusing to destroy storage without a prefix"
            )

        for blob in self.client.list_blobs(
            self.bucket, prefix=self.prefix
        ):
            blob.delete()

    def __str__(self) -> str:
        return f"gcs.Storage(bucket={self.bucket.name}, prefix={self.prefix!r})"
