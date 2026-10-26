import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from conftest import PASSWORD, set_csrf_header
from users.models import User

pytestmark = pytest.mark.django_db


# --- CSRF ---------------------------------------------------------------------------------


def test_csrf_endpoint_sets_cookie(api_client):
    response = api_client.get(reverse('auth-csrf'))

    assert response.status_code == 204
    assert 'csrftoken' in response.cookies


# --- Signup -------------------------------------------------------------------------------


def test_signup_creates_user_without_role(csrf_client):
    response = csrf_client.post(
        reverse('auth-signup'), {'username': 'maria', 'password': PASSWORD}, format='json'
    )

    assert response.status_code == 201
    assert response.json()['username'] == 'maria'
    assert response.json()['role'] is None
    assert 'password' not in response.json()

    user = User.objects.get(username='maria')
    assert user.role == ''
    assert user.check_password(PASSWORD)
    assert user.password != PASSWORD


def test_signup_does_not_log_in(csrf_client):
    csrf_client.post(
        reverse('auth-signup'), {'username': 'maria', 'password': PASSWORD}, format='json'
    )

    assert csrf_client.get(reverse('auth-me')).status_code == 403


def test_signup_rejects_weak_password(csrf_client):
    response = csrf_client.post(
        reverse('auth-signup'), {'username': 'maria', 'password': '123'}, format='json'
    )

    assert response.status_code == 400
    assert 'Parola este prea scurtă' in ' '.join(response.json()['password'])
    assert not User.objects.filter(username='maria').exists()


def test_signup_rejects_duplicate_username(csrf_client, user):
    response = csrf_client.post(
        reverse('auth-signup'), {'username': user.username, 'password': PASSWORD}, format='json'
    )

    assert response.status_code == 400
    assert 'username' in response.json()


def test_signup_requires_csrf_token():
    client = APIClient(enforce_csrf_checks=True)
    response = client.post(
        reverse('auth-signup'), {'username': 'maria', 'password': PASSWORD}, format='json'
    )

    assert response.status_code == 403
    assert not User.objects.filter(username='maria').exists()


# --- Login --------------------------------------------------------------------------------


def test_login_starts_session(csrf_client, user):
    response = csrf_client.post(
        reverse('auth-login'), {'username': 'ion', 'password': PASSWORD}, format='json'
    )

    assert response.status_code == 200
    assert response.json()['username'] == 'ion'
    assert 'sessionid' in response.cookies
    assert csrf_client.get(reverse('auth-me')).json()['username'] == 'ion'


def test_login_rejects_wrong_password(csrf_client, user):
    response = csrf_client.post(
        reverse('auth-login'), {'username': 'ion', 'password': 'gresita'}, format='json'
    )

    assert response.status_code == 400
    assert response.json() == {'non_field_errors': ['Nume de utilizator sau parolă greșită.']}


def test_login_rejects_unknown_user_with_same_message(csrf_client):
    response = csrf_client.post(
        reverse('auth-login'), {'username': 'nimeni', 'password': PASSWORD}, format='json'
    )

    assert response.status_code == 400
    assert response.json() == {'non_field_errors': ['Nume de utilizator sau parolă greșită.']}


def test_login_rejects_inactive_user(csrf_client, user):
    user.is_active = False
    user.save()

    response = csrf_client.post(
        reverse('auth-login'), {'username': 'ion', 'password': PASSWORD}, format='json'
    )

    assert response.status_code == 400


def test_login_requires_csrf_token(user):
    client = APIClient(enforce_csrf_checks=True)
    response = client.post(
        reverse('auth-login'), {'username': 'ion', 'password': PASSWORD}, format='json'
    )

    assert response.status_code == 403


# --- Me -----------------------------------------------------------------------------------


def test_me_requires_authentication(api_client):
    assert api_client.get(reverse('auth-me')).status_code == 403


def test_me_returns_current_user(api_client, user):
    api_client.force_authenticate(user)

    response = api_client.get(reverse('auth-me'))

    assert response.status_code == 200
    assert response.json() == {
        'id': str(user.id),
        'username': 'ion',
        'email': '',
        'first_name': '',
        'last_name': '',
        'role': None,
    }


@pytest.mark.parametrize('role', [User.Role.ADMIN, User.Role.USER])
def test_me_returns_role(api_client, user, role):
    user.role = role
    user.save()
    api_client.force_authenticate(user)

    assert api_client.get(reverse('auth-me')).json()['role'] == role


# --- Logout -------------------------------------------------------------------------------


def test_logout_ends_session(csrf_client, user):
    csrf_client.post(
        reverse('auth-login'), {'username': 'ion', 'password': PASSWORD}, format='json'
    )
    set_csrf_header(csrf_client)  # Django schimbă token-ul CSRF la login

    response = csrf_client.post(reverse('auth-logout'))

    assert response.status_code == 204
    assert csrf_client.get(reverse('auth-me')).status_code == 403


def test_logout_requires_csrf_token(csrf_client, user):
    csrf_client.post(
        reverse('auth-login'), {'username': 'ion', 'password': PASSWORD}, format='json'
    )
    csrf_client.credentials()  # fără header CSRF

    response = csrf_client.post(reverse('auth-logout'))

    assert response.status_code == 403
    assert csrf_client.get(reverse('auth-me')).status_code == 200


def test_logout_requires_authentication(csrf_client):
    assert csrf_client.post(reverse('auth-logout')).status_code == 403


# --- Sesiune ------------------------------------------------------------------------------


def test_session_expires_after_one_day_of_inactivity(settings):
    assert settings.SESSION_COOKIE_AGE == 60 * 60 * 24
    assert settings.SESSION_SAVE_EVERY_REQUEST is True
