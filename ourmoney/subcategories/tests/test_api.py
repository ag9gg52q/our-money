import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from categories.models import Category
from households.services import create_household, join_household
from subcategories.models import Subcategory
from users.models import User

pytestmark = pytest.mark.django_db


def list_url(category_id):
    return reverse('subcategory-list', args=[category_id])


def detail_url(subcategory_id):
    return reverse('subcategory-detail', args=[subcategory_id])


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


@pytest.fixture
def subcategory(category):
    return Subcategory.objects.create(category=category, name='Lactate')


def client_for(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


# Listare


def test_list_returns_category_subcategories_sorted(admin, category):
    Subcategory.objects.create(category=category, name='Pâine')
    Subcategory.objects.create(category=category, name='Lactate', is_active=False)

    response = client_for(admin).get(list_url(category.id))

    assert response.status_code == 200
    assert [(s['name'], s['is_active']) for s in response.json()] == [
        ('Lactate', False),
        ('Pâine', True),
    ]


def test_list_response_format(admin, subcategory):
    response = client_for(admin).get(list_url(subcategory.category_id))

    assert response.json() == [{'id': str(subcategory.id), 'name': 'Lactate', 'is_active': True}]


def test_list_hides_subcategories_of_other_categories(admin, category, subcategory):
    other = Category.objects.create(household=admin.household, name='Transport')

    response = client_for(admin).get(list_url(other.id))

    assert response.status_code == 200
    assert response.json() == []


def test_member_can_list(member, subcategory):
    response = client_for(member).get(list_url(subcategory.category_id))

    assert response.status_code == 200
    assert [s['id'] for s in response.json()] == [str(subcategory.id)]


def test_list_other_household_category_returns_404(other_admin, subcategory):
    response = client_for(other_admin).get(list_url(subcategory.category_id))

    assert response.status_code == 404


def test_list_unknown_category_returns_404(admin):
    response = client_for(admin).get(list_url('00000000-0000-0000-0000-000000000000'))

    assert response.status_code == 404


def test_list_without_household_returns_403(user, category):
    response = client_for(user).get(list_url(category.id))

    assert response.status_code == 403
    assert response.json()['detail'] == 'Nu faci parte dintr-o gospodărie.'


def test_list_unauthenticated_returns_403(api_client, category):
    assert api_client.get(list_url(category.id)).status_code == 403


# Adăugare


def test_create_subcategory(admin, category, csrf_client):
    csrf_client.force_login(admin)

    response = csrf_client.post(list_url(category.id), {'name': '  Lactate  '}, format='json')

    assert response.status_code == 201
    subcategory = Subcategory.objects.get()
    assert response.json() == {'id': str(subcategory.id), 'name': 'Lactate', 'is_active': True}
    assert subcategory.category == category


@pytest.mark.parametrize('name', ['', '   ', 'a' * 51])
def test_create_invalid_name_returns_400(admin, category, name):
    response = client_for(admin).post(list_url(category.id), {'name': name}, format='json')

    assert response.status_code == 400
    assert 'name' in response.json()
    assert Subcategory.objects.count() == 0


def test_create_duplicate_name_ignores_case(admin, subcategory):
    response = client_for(admin).post(
        list_url(subcategory.category_id), {'name': 'LACTATE'}, format='json'
    )

    assert response.status_code == 400
    assert response.json()['name'] == ['Există deja o subcategorie cu acest nume în categorie.']
    assert Subcategory.objects.count() == 1


def test_same_name_allowed_in_another_category(admin, subcategory):
    other = Category.objects.create(household=admin.household, name='Transport')

    response = client_for(admin).post(list_url(other.id), {'name': 'Lactate'}, format='json')

    assert response.status_code == 201
    assert other.subcategories.count() == 1


def test_create_ignores_category_sent_by_client(admin, category):
    other = Category.objects.create(household=admin.household, name='Transport')

    response = client_for(admin).post(
        list_url(category.id), {'name': 'Lactate', 'category': str(other.id)}, format='json'
    )

    assert response.status_code == 201
    assert Subcategory.objects.get().category == category


def test_create_in_other_household_category_returns_404(other_admin, category):
    response = client_for(other_admin).post(
        list_url(category.id), {'name': 'Lactate'}, format='json'
    )

    assert response.status_code == 404
    assert Subcategory.objects.count() == 0


def test_member_cannot_create(member, category):
    response = client_for(member).post(list_url(category.id), {'name': 'Lactate'}, format='json')

    assert response.status_code == 403
    assert response.json()['detail'] == 'Doar administratorul gospodăriei poate face modificări.'
    assert Subcategory.objects.count() == 0


def test_create_requires_csrf(admin, category):
    client = APIClient(enforce_csrf_checks=True)
    client.force_login(admin)

    response = client.post(list_url(category.id), {'name': 'Lactate'}, format='json')

    assert response.status_code == 403
    assert Subcategory.objects.count() == 0


# Editare


def test_deactivate_subcategory(admin, subcategory, csrf_client):
    csrf_client.force_login(admin)

    response = csrf_client.patch(detail_url(subcategory.id), {'is_active': False}, format='json')

    assert response.status_code == 200
    assert response.json() == {'id': str(subcategory.id), 'name': 'Lactate', 'is_active': False}
    subcategory.refresh_from_db()
    assert subcategory.is_active is False
    assert subcategory.name == 'Lactate'


def test_rename_subcategory(admin, subcategory):
    response = client_for(admin).patch(
        detail_url(subcategory.id), {'name': 'Brânzeturi'}, format='json'
    )

    assert response.status_code == 200
    subcategory.refresh_from_db()
    assert subcategory.name == 'Brânzeturi'
    assert subcategory.is_active is True


def test_rename_keeping_own_name_is_allowed(admin, subcategory):
    response = client_for(admin).patch(
        detail_url(subcategory.id), {'name': 'LACTATE'}, format='json'
    )

    assert response.status_code == 200
    subcategory.refresh_from_db()
    assert subcategory.name == 'LACTATE'


def test_rename_to_existing_name_returns_400(admin, category, subcategory):
    Subcategory.objects.create(category=category, name='Pâine')

    response = client_for(admin).patch(detail_url(subcategory.id), {'name': 'pâine'}, format='json')

    assert response.status_code == 400
    assert 'name' in response.json()
    subcategory.refresh_from_db()
    assert subcategory.name == 'Lactate'


def test_rename_to_name_used_in_another_category_is_allowed(admin, subcategory):
    other = Category.objects.create(household=admin.household, name='Transport')
    Subcategory.objects.create(category=other, name='Altele')

    response = client_for(admin).patch(
        detail_url(subcategory.id), {'name': 'Altele'}, format='json'
    )

    assert response.status_code == 200


def test_edit_ignores_category_sent_by_client(admin, subcategory):
    other = Category.objects.create(household=admin.household, name='Transport')

    response = client_for(admin).patch(
        detail_url(subcategory.id), {'category': str(other.id)}, format='json'
    )

    assert response.status_code == 200
    subcategory.refresh_from_db()
    assert subcategory.category_id != other.id


def test_other_household_cannot_edit(other_admin, subcategory):
    response = client_for(other_admin).patch(
        detail_url(subcategory.id), {'is_active': False}, format='json'
    )

    assert response.status_code == 404
    subcategory.refresh_from_db()
    assert subcategory.is_active is True


def test_member_cannot_edit(member, subcategory):
    response = client_for(member).patch(
        detail_url(subcategory.id), {'is_active': False}, format='json'
    )

    assert response.status_code == 403
    subcategory.refresh_from_db()
    assert subcategory.is_active is True


def test_edit_requires_csrf(admin, subcategory):
    client = APIClient(enforce_csrf_checks=True)
    client.force_login(admin)

    response = client.patch(detail_url(subcategory.id), {'is_active': False}, format='json')

    assert response.status_code == 403
    subcategory.refresh_from_db()
    assert subcategory.is_active is True


def test_edit_invalid_id_returns_404(admin):
    response = client_for(admin).patch('/api/v1/subcategories/abc/', {}, format='json')

    assert response.status_code == 404


# Operații care nu există


def test_delete_not_allowed(admin, subcategory):
    response = client_for(admin).delete(detail_url(subcategory.id))

    assert response.status_code == 405
    assert Subcategory.objects.filter(pk=subcategory.pk).exists()


def test_put_not_allowed(admin, subcategory):
    response = client_for(admin).put(
        detail_url(subcategory.id), {'name': 'X', 'is_active': True}, format='json'
    )

    assert response.status_code == 405
