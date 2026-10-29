import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from categories.models import Category
from households.services import create_household, join_household
from users.models import User

pytestmark = pytest.mark.django_db
LIST_URL = reverse('category-list')


def detail_url(category_id):
    return reverse('category-detail', args=[category_id])


@pytest.fixture
def admin():
    user = User.objects.create_user(username='admin', password='x')
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


@pytest.fixture
def category(admin):
    return Category.objects.create(household=admin.household, name='Alimente')


def client_for(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


# Listare


def test_list_returns_household_categories_sorted(admin):
    Category.objects.create(household=admin.household, name='Transport')
    Category.objects.create(household=admin.household, name='Alimente', is_active=False)

    response = client_for(admin).get(LIST_URL)

    assert response.status_code == 200
    assert [(c['name'], c['is_active']) for c in response.json()] == [
        ('Alimente', False),
        ('Transport', True),
    ]


def test_list_response_format(admin, category):
    response = client_for(admin).get(LIST_URL)

    assert response.json() == [{'id': str(category.id), 'name': 'Alimente', 'is_active': True}]


def test_member_can_list(member, category):
    response = client_for(member).get(LIST_URL)

    assert response.status_code == 200
    assert [c['id'] for c in response.json()] == [str(category.id)]


def test_list_hides_other_household_categories(other_admin, category):
    response = client_for(other_admin).get(LIST_URL)

    assert response.status_code == 200
    assert response.json() == []


def test_list_without_household_returns_403(user):
    response = client_for(user).get(LIST_URL)

    assert response.status_code == 403
    assert response.json()['detail'] == 'Nu faci parte dintr-o gospodărie.'


def test_list_unauthenticated_returns_403(api_client):
    assert api_client.get(LIST_URL).status_code == 403


# Adăugare


def test_create_category(admin, csrf_client):
    csrf_client.force_login(admin)

    response = csrf_client.post(LIST_URL, {'name': '  Alimente  '}, format='json')

    assert response.status_code == 201
    category = Category.objects.get()
    assert response.json() == {'id': str(category.id), 'name': 'Alimente', 'is_active': True}
    assert category.household == admin.household


@pytest.mark.parametrize('name', ['', '   ', 'a' * 51])
def test_create_invalid_name_returns_400(admin, name):
    response = client_for(admin).post(LIST_URL, {'name': name}, format='json')

    assert response.status_code == 400
    assert 'name' in response.json()
    assert Category.objects.count() == 0


def test_create_duplicate_name_ignores_case(admin, category):
    response = client_for(admin).post(LIST_URL, {'name': 'ALIMENTE'}, format='json')

    assert response.status_code == 400
    assert response.json()['name'] == ['Există deja o categorie cu acest nume în gospodărie.']
    assert Category.objects.count() == 1


def test_same_name_allowed_in_another_household(other_admin, category):
    response = client_for(other_admin).post(LIST_URL, {'name': 'Alimente'}, format='json')

    assert response.status_code == 201
    assert other_admin.household.categories.count() == 1


def test_create_ignores_household_sent_by_client(admin, other_admin):
    response = client_for(admin).post(
        LIST_URL, {'name': 'Alimente', 'household': str(other_admin.household.id)}, format='json'
    )

    assert response.status_code == 201
    assert Category.objects.get().household == admin.household


def test_member_cannot_create(member):
    response = client_for(member).post(LIST_URL, {'name': 'Alimente'}, format='json')

    assert response.status_code == 403
    assert response.json()['detail'] == 'Doar administratorul gospodăriei poate face modificări.'
    assert Category.objects.count() == 0


def test_create_requires_csrf(admin):
    client = APIClient(enforce_csrf_checks=True)
    client.force_login(admin)

    response = client.post(LIST_URL, {'name': 'Alimente'}, format='json')

    assert response.status_code == 403
    assert Category.objects.count() == 0


# Editare


def test_deactivate_category(admin, category, csrf_client):
    csrf_client.force_login(admin)

    response = csrf_client.patch(detail_url(category.id), {'is_active': False}, format='json')

    assert response.status_code == 200
    assert response.json() == {'id': str(category.id), 'name': 'Alimente', 'is_active': False}
    category.refresh_from_db()
    assert category.is_active is False
    assert category.name == 'Alimente'


def test_rename_category(admin, category):
    response = client_for(admin).patch(detail_url(category.id), {'name': 'Mâncare'}, format='json')

    assert response.status_code == 200
    category.refresh_from_db()
    assert category.name == 'Mâncare'
    assert category.is_active is True


def test_rename_keeping_own_name_is_allowed(admin, category):
    response = client_for(admin).patch(detail_url(category.id), {'name': 'ALIMENTE'}, format='json')

    assert response.status_code == 200
    category.refresh_from_db()
    assert category.name == 'ALIMENTE'


def test_rename_to_existing_name_returns_400(admin, category):
    Category.objects.create(household=admin.household, name='Transport')

    response = client_for(admin).patch(
        detail_url(category.id), {'name': 'transport'}, format='json'
    )

    assert response.status_code == 400
    assert 'name' in response.json()
    category.refresh_from_db()
    assert category.name == 'Alimente'


def test_other_household_cannot_edit(other_admin, category):
    response = client_for(other_admin).patch(
        detail_url(category.id), {'is_active': False}, format='json'
    )

    assert response.status_code == 404
    category.refresh_from_db()
    assert category.is_active is True


def test_member_cannot_edit(member, category):
    response = client_for(member).patch(
        detail_url(category.id), {'is_active': False}, format='json'
    )

    assert response.status_code == 403
    category.refresh_from_db()
    assert category.is_active is True


def test_edit_requires_csrf(admin, category):
    client = APIClient(enforce_csrf_checks=True)
    client.force_login(admin)

    response = client.patch(detail_url(category.id), {'is_active': False}, format='json')

    assert response.status_code == 403
    category.refresh_from_db()
    assert category.is_active is True


def test_edit_invalid_id_returns_404(admin):
    response = client_for(admin).patch('/api/v1/categories/abc/', {}, format='json')

    assert response.status_code == 404


# Operații care nu există


def test_delete_not_allowed(admin, category):
    response = client_for(admin).delete(detail_url(category.id))

    assert response.status_code == 405
    assert Category.objects.filter(pk=category.pk).exists()


def test_put_not_allowed(admin, category):
    response = client_for(admin).put(
        detail_url(category.id), {'name': 'X', 'is_active': True}, format='json'
    )

    assert response.status_code == 405
