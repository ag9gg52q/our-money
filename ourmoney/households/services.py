from django.db import transaction

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
