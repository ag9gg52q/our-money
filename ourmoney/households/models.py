import secrets
import uuid

from django.db import models

INVITE_CODE_ALPHABET = 'ABCDEFGHJKMNPQRSTUVWXYZ23456789'


def generate_invite_code():
    chars = ''.join(secrets.choice(INVITE_CODE_ALPHABET) for _ in range(8))
    return f'{chars[:4]}-{chars[4:]}'


class Household(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    invite_code = models.CharField(
        max_length=9, default=generate_invite_code, unique=True, editable=False
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
