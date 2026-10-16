from django.urls import reverse
from rest_framework.test import APIClient


def test_health_returns_ok():
    client = APIClient()

    response = client.get(reverse('health'))

    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}


def test_health_rejects_post():
    client = APIClient()

    response = client.post(reverse('health'))

    assert response.status_code == 405
