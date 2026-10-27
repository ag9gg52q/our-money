import uuid

from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models


class CustomUserManager(UserManager):
    """Fără comportament propriu; păstrat pentru că migrația users 0001 îl referă.

    Rolul nu se mai dă din `createsuperuser`: devine `admin` doar cine creează o gospodărie.
    """


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Administrator'
        USER = 'user', 'Utilizator'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(max_length=10, choices=Role.choices, blank=True, default='')
    household = models.ForeignKey(
        'households.Household',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='members',
    )
    objects = CustomUserManager()

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN
