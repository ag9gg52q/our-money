import pytest
from rest_framework.test import APIClient

PASSWORD = 'OurMoney2026!x'


def set_csrf_header(client):
    """Pune token-ul CSRF din cookie în header, ca un browser care folosește apiFetch."""
    client.credentials(HTTP_X_CSRFTOKEN=client.cookies['csrftoken'].value)


@pytest.fixture
def api_client():
    """Client fără verificare CSRF — pentru cereri GET și cazuri simple."""
    return APIClient()


@pytest.fixture
def csrf_client():
    """Client cu verificare CSRF activă, care are deja cookie-ul și header-ul CSRF."""
    client = APIClient(enforce_csrf_checks=True)
    client.get('/api/v1/auth/csrf/')
    set_csrf_header(client)
    return client


@pytest.fixture
def user(django_user_model):
    return django_user_model.objects.create_user(username='ion', password=PASSWORD)
