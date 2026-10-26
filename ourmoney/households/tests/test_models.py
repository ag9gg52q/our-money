import pytest

from households.models import INVITE_CODE_ALPHABET, Household, generate_invite_code
from users.models import User

pytestmark = pytest.mark.django_db


def test_invite_code_format():
    code = generate_invite_code()

    assert len(code) == 9
    assert code[4] == '-'
    assert all(char in INVITE_CODE_ALPHABET for char in code.replace('-', ''))


def test_new_household_gets_invite_code():
    household = Household.objects.create(name='Familia Popescu')

    assert len(household.invite_code) == 9


def test_households_get_different_invite_codes():
    first = Household.objects.create(name='Prima')
    second = Household.objects.create(name='A doua')

    assert first.invite_code != second.invite_code


def test_user_belongs_to_household():
    household = Household.objects.create(name='Familia Popescu')
    user = User.objects.create_user(username='ion', password='x', household=household)

    assert list(household.members.all()) == [user]


def test_deleting_household_removes_members_household_and_role():
    household = Household.objects.create(name='Familia Popescu')
    user = User.objects.create_user(
        username='ion', password='x', household=household, role=User.Role.ADMIN
    )

    household.delete()
    user.refresh_from_db()

    assert user.household is None
    assert user.role == ''
