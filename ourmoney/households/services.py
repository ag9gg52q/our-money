from django.db import transaction
from rest_framework.exceptions import ValidationError

from users.models import User

from .models import Household


@transaction.atomic
def create_household(*, user, name):
    household = Household.objects.create(name=name)
    user.household = household
    user.role = User.Role.ADMIN
    user.save(update_fields=['household', 'role'])
    return household


def join_household(*, user, household):
    user.household = household
    user.role = User.Role.USER
    user.save(update_fields=['household', 'role'])
    return household


def make_admin(*, member):
    if member.role == User.Role.ADMIN:
        raise ValidationError('Membrul este deja administrator')
    member.role = User.Role.ADMIN
    member.save(update_fields=['role'])
    return member


def update_household(*, household, name):
    household.name = name
    household.save(update_fields=['name'])
    return household
