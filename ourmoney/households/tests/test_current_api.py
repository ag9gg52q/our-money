import uuid

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from households.services import create_household, join_household
from users.models import User

pytestmark = pytest.mark.django_db
CURRENT_URL = reverse('household-current')


def make_admin_url(member_id):
    return reverse('household-member-make-admin', args=[member_id])


@pytest.fixture
def admin():
    user = User.objects.create_user(username='admin', password='x', first_name='Ion')
    create_household(user=user, name='Familia Popescu')
    return user


@pytest.fixture
def member(admin):
    user = User.objects.create_user(username='membru', password='x')
    join_household(user=user, household=admin.household)
    return user


@pytest.fixture
def other_admin():
    user = User.objects.create_user(username='vecin', password='x')
    create_household(user=user, name='Familia Ionescu')
    return user


def client_for(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


# Citire


def test_admin_gets_household_with_invite_code_and_members(admin, member):
    response = client_for(admin).get(CURRENT_URL)

    assert response.status_code == 200
    assert response.json() == {
        'id': str(admin.household.id),
        'name': 'Familia Popescu',
        'invite_code': admin.household.invite_code,
        'members': [
            {
                'id': str(admin.id),
                'username': 'admin',
                'first_name': 'Ion',
                'last_name': '',
                'role': 'admin',
            },
            {
                'id': str(member.id),
                'username': 'membru',
                'first_name': '',
                'last_name': '',
                'role': 'user',
            },
        ],
    }


def test_members_ordered_admins_first_then_by_username(admin, member):
    ana = User.objects.create_user(username='ana', password='x')
    join_household(user=ana, household=admin.household)

    response = client_for(admin).get(CURRENT_URL)

    assert [m['username'] for m in response.json()['members']] == ['admin', 'ana', 'membru']


def test_member_gets_household_without_invite_code(member):
    response = client_for(member).get(CURRENT_URL)

    assert response.status_code == 200
    assert response.json()['invite_code'] is None
    assert len(response.json()['members']) == 2


def test_members_of_other_household_are_hidden(admin, other_admin):
    response = client_for(admin).get(CURRENT_URL)

    assert [m['username'] for m in response.json()['members']] == ['admin']


def test_get_without_household_returns_403(user):
    response = client_for(user).get(CURRENT_URL)

    assert response.status_code == 403
    assert response.json()['detail'] == 'Nu faci parte dintr-o gospodărie.'


def test_get_unauthenticated_returns_403(api_client):
    assert api_client.get(CURRENT_URL).status_code == 403


# Redenumire


def test_admin_renames_household(admin, csrf_client):
    csrf_client.force_login(admin)

    response = csrf_client.patch(CURRENT_URL, {'name': '  Familia Nouă  '}, format='json')

    assert response.status_code == 200
    assert response.json()['name'] == 'Familia Nouă'
    assert response.json()['invite_code'] == admin.household.invite_code
    admin.household.refresh_from_db()
    assert admin.household.name == 'Familia Nouă'


@pytest.mark.parametrize('name', ['', '   ', 'a' * 101])
def test_rename_invalid_name_returns_400(admin, name):
    response = client_for(admin).patch(CURRENT_URL, {'name': name}, format='json')

    assert response.status_code == 400
    assert 'name' in response.json()
    admin.household.refresh_from_db()
    assert admin.household.name == 'Familia Popescu'


def test_patch_without_name_keeps_name(admin):
    response = client_for(admin).patch(CURRENT_URL, {}, format='json')

    assert response.status_code == 200
    assert response.json()['name'] == 'Familia Popescu'


def test_patch_ignores_invite_code_sent_by_client(admin):
    old_code = admin.household.invite_code

    response = client_for(admin).patch(
        CURRENT_URL, {'name': 'Familie', 'invite_code': 'AAAA-BBBB'}, format='json'
    )

    assert response.status_code == 200
    admin.household.refresh_from_db()
    assert admin.household.invite_code == old_code


def test_member_cannot_rename(member):
    response = client_for(member).patch(CURRENT_URL, {'name': 'Altceva'}, format='json')

    assert response.status_code == 403
    assert response.json()['detail'] == 'Doar administratorul gospodăriei poate face modificări.'
    member.household.refresh_from_db()
    assert member.household.name == 'Familia Popescu'


def test_rename_without_household_returns_403(user):
    response = client_for(user).patch(CURRENT_URL, {'name': 'Familie'}, format='json')

    assert response.status_code == 403


def test_rename_requires_csrf(admin):
    client = APIClient(enforce_csrf_checks=True)
    client.force_login(admin)

    response = client.patch(CURRENT_URL, {'name': 'Altceva'}, format='json')

    assert response.status_code == 403
    admin.household.refresh_from_db()
    assert admin.household.name == 'Familia Popescu'


# Promovare la admin


def test_admin_makes_member_admin(admin, member, csrf_client):
    csrf_client.force_login(admin)

    response = csrf_client.post(make_admin_url(member.id))

    assert response.status_code == 200
    assert response.json() == {
        'id': str(member.id),
        'username': 'membru',
        'first_name': '',
        'last_name': '',
        'role': 'admin',
    }
    member.refresh_from_db()
    assert member.role == User.Role.ADMIN
    assert member.household == admin.household


def test_make_admin_on_admin_returns_400(admin, member):
    member.role = User.Role.ADMIN
    member.save()

    response = client_for(admin).post(make_admin_url(member.id))

    assert response.status_code == 400
    assert response.json() == {'non_field_errors': ['Membrul este deja administrator.']}


def test_admin_cannot_make_self_admin_again(admin):
    response = client_for(admin).post(make_admin_url(admin.id))

    assert response.status_code == 400
    admin.refresh_from_db()
    assert admin.role == User.Role.ADMIN


def test_member_cannot_make_admin(admin, member):
    ana = User.objects.create_user(username='ana', password='x')
    join_household(user=ana, household=admin.household)

    response = client_for(member).post(make_admin_url(ana.id))

    assert response.status_code == 403
    ana.refresh_from_db()
    assert ana.role == User.Role.USER


def test_make_admin_on_other_household_member_returns_404(admin, other_admin):
    neighbour = User.objects.create_user(username='vecina', password='x')
    join_household(user=neighbour, household=other_admin.household)

    response = client_for(admin).post(make_admin_url(neighbour.id))

    assert response.status_code == 404
    neighbour.refresh_from_db()
    assert neighbour.role == User.Role.USER


def test_make_admin_unknown_id_returns_404(admin):
    response = client_for(admin).post(make_admin_url(uuid.uuid4()))

    assert response.status_code == 404


def test_make_admin_requires_csrf(admin, member):
    client = APIClient(enforce_csrf_checks=True)
    client.force_login(admin)

    response = client.post(make_admin_url(member.id))

    assert response.status_code == 403
    member.refresh_from_db()
    assert member.role == User.Role.USER


def test_make_admin_get_not_allowed(admin, member):
    response = client_for(admin).get(make_admin_url(member.id))

    assert response.status_code == 405
