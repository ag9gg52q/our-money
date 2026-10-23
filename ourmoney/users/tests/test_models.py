import pytest

from users.models import User

pytestmark = pytest.mark.django_db


def test_new_user_has_no_role():
    user = User.objects.create_user(username='ion', password='OurMoney2026!x')

    assert user.role == ''
    assert user.is_admin is False


def test_superuser_gets_admin_role():
    user = User.objects.create_superuser(username='root', password='OurMoney2026!x')

    assert user.role == User.Role.ADMIN
    assert user.is_admin is True


def test_user_role_is_not_admin():
    user = User.objects.create_user(username='ion', password='x', role=User.Role.USER)

    assert user.is_admin is False


def test_id_is_uuid():
    user = User.objects.create_user(username='ion', password='OurMoney2026!x')

    assert len(str(user.id)) == 36
