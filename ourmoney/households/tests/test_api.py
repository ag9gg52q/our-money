import pytest
from rest_framework.test import APIClient

from households.models import Household
from users.models import User

pytestmark = pytest.mark.django_db
URL = '/api/v1/households/'
JOIN_URL = '/api/v1/households/join/'
ME_URL = '/api/v1/auth/me/'


@pytest.fixture
def logged_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def household():
    return Household.objects.create(name='Familia Popescu')


def test_create_household(logged_client, user):
    response = logged_client.post(URL, {'name': 'Familia Popescu'}, format='json')

    assert response.status_code == 201
    assert response.data['name'] == 'Familia Popescu'
    assert len(response.data['invite_code']) == 9
    user.refresh_from_db()
    assert user.household.name == 'Familia Popescu'
    assert user.role == User.Role.ADMIN


def test_create_household_trims_name(logged_client, user):
    response = logged_client.post(URL, {'name': '   Familia   '}, format='json')

    assert response.status_code == 201
    assert response.data['name'] == 'Familia'
    user.refresh_from_db()
    assert user.household.name == 'Familia'


@pytest.mark.parametrize('name', ['', '   ', 'a' * 101])
def test_create_household_invalid_name_returns_400(logged_client, user, name):
    response = logged_client.post(URL, {'name': name}, format='json')

    assert response.status_code == 400
    assert 'name' in response.data
    assert Household.objects.count() == 0
    user.refresh_from_db()
    assert user.role == ''


def test_create_household_when_user_already_in_household(logged_client, user):
    existing = Household.objects.create(name='Familie')
    user.household = existing
    user.role = User.Role.USER
    user.save()

    response = logged_client.post(URL, {'name': 'Familie Doi'}, format='json')

    assert response.status_code == 400
    assert response.data['non_field_errors'] == ['Faci deja parte dintr-o gospodărie.']
    assert Household.objects.count() == 1
    user.refresh_from_db()
    assert user.household == existing
    assert user.role == User.Role.USER


def test_create_household_unauthenticated(api_client):
    response = api_client.post(URL, {'name': 'Familie'}, format='json')

    assert response.status_code == 403
    assert Household.objects.count() == 0


def test_create_household_requires_csrf(user):
    client = APIClient(enforce_csrf_checks=True)
    client.force_login(user)

    response = client.post(URL, {'name': 'Familie'}, format='json')

    assert response.status_code == 403
    assert Household.objects.count() == 0


def test_join_household(logged_client, user, household):
    response = logged_client.post(JOIN_URL, {'invite_code': household.invite_code}, format='json')

    assert response.status_code == 200
    assert response.json() == {'id': str(household.id), 'name': 'Familia Popescu'}
    user.refresh_from_db()
    assert user.household == household
    assert user.role == User.Role.USER


@pytest.mark.parametrize(
    'transform',
    [
        lambda code: code.lower(),
        lambda code: code.replace('-', ''),
        lambda code: f'  {code}  ',
        lambda code: code.replace('-', ' ').lower(),
    ],
    ids=['lowercase', 'without-dash', 'surrounding-spaces', 'space-instead-of-dash'],
)
def test_join_household_normalizes_code(logged_client, user, household, transform):
    response = logged_client.post(
        JOIN_URL, {'invite_code': transform(household.invite_code)}, format='json'
    )

    assert response.status_code == 200
    user.refresh_from_db()
    assert user.household == household


@pytest.mark.parametrize('code', ['ZZZZ-9999', 'ABC', ''])
def test_join_household_invalid_code_returns_400(logged_client, user, household, code):
    response = logged_client.post(JOIN_URL, {'invite_code': code}, format='json')

    assert response.status_code == 400
    assert 'invite_code' in response.data
    user.refresh_from_db()
    assert user.household is None
    assert user.role == ''


def test_join_household_unknown_code_message(logged_client, household):
    response = logged_client.post(JOIN_URL, {'invite_code': 'ZZZZ-9999'}, format='json')

    assert response.data['invite_code'] == ['Codul de invitație nu este valid.']


def test_join_household_when_user_already_in_household(logged_client, user, household):
    existing = Household.objects.create(name='Familie')
    user.household = existing
    user.role = User.Role.ADMIN
    user.save()

    response = logged_client.post(JOIN_URL, {'invite_code': household.invite_code}, format='json')

    assert response.status_code == 400
    assert response.data['non_field_errors'] == ['Faci deja parte dintr-o gospodărie.']
    user.refresh_from_db()
    assert user.household == existing
    assert user.role == User.Role.ADMIN


def test_join_household_unauthenticated(api_client, household):
    response = api_client.post(JOIN_URL, {'invite_code': household.invite_code}, format='json')

    assert response.status_code == 403
    assert household.members.count() == 0


def test_join_household_requires_csrf(user, household):
    client = APIClient(enforce_csrf_checks=True)
    client.force_login(user)

    response = client.post(JOIN_URL, {'invite_code': household.invite_code}, format='json')

    assert response.status_code == 403
    user.refresh_from_db()
    assert user.household is None


def test_me_for_admin_includes_invite_code(logged_client):
    created = logged_client.post(URL, {'name': 'Familie'}, format='json')

    response = logged_client.get(ME_URL)

    assert response.status_code == 200
    assert response.data['role'] == 'admin'
    assert response.json()['household'] == {
        'id': created.json()['id'],
        'name': 'Familie',
        'invite_code': created.data['invite_code'],
    }


def test_me_for_member_hides_invite_code(logged_client, user):
    household = Household.objects.create(name='Familie')
    user.household = household
    user.role = User.Role.USER
    user.save()

    response = logged_client.get(ME_URL)

    assert response.json()['household'] == {'id': str(household.id), 'name': 'Familie'}


def test_me_without_household(logged_client):
    response = logged_client.get(ME_URL)

    assert response.data['household'] is None
