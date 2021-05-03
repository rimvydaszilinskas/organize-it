import uuid

from django.db import models


class BaseModel(models.Model):
    uuid = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        db_index=True,
        editable=False
    )

    class Meta:
        abstract = True
