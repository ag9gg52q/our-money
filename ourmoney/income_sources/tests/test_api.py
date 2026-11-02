import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from households.services import create_household, join_household
from income_sources.models import IncomeSource
from users.models import User

pytestmark = pytest.mark.django_db
LIST_URL = reverse('income-source-list')


def detail_url(income_source_id):
    return reverse('income-source-detail', args=[income_source_id])


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
def income_source(admin):
    return IncomeSource.objects.create(household=admin.household, name='Bonus')


def client_for(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


# Listare


def test_list_returns_household_income_sources_sorted(admin):
    IncomeSource.objects.create(household=admin.household, name='Salariu')
    IncomeSource.objects.create(household=admin.household, name='Bonus', is_active=False)

    response = client_for(admin).get(LIST_URL)

    assert response.status_code == 200
    assert [(c['name'], c['is_active']) for c in response.json()] == [
        ('Bonus', False),
        ('Salariu', True),
    ]


def test_list_response_format(admin, income_source):
    response = client_for(admin).get(LIST_URL)

    assert response.json() == [{'id': str(income_source.id), 'name': 'Bonus', 'is_active': True}]


def test_member_can_list(member, income_source):
    response = client_for(member).get(LIST_URL)

    assert response.status_code == 200
    assert [c['id'] for c in response.json()] == [str(income_source.id)]


def test_list_hides_other_household_income_sources(other_admin, income_source):
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


def test_create_income_source(admin, csrf_client):
    csrf_client.force_login(admin)

    response = csrf_client.post(LIST_URL, {'name': '  Bonus  '}, format='json')

    assert response.status_code == 201
    income_source = IncomeSource.objects.get()
    assert response.json() == {'id': str(income_source.id), 'name': 'Bonus', 'is_active': True}
    assert income_source.household == admin.household


@pytest.mark.parametrize('name', ['', '   ', 'a' * 51])
def test_create_invalid_name_returns_400(admin, name):
    response = client_for(admin).post(LIST_URL, {'name': name}, format='json')

    assert response.status_code == 400
    assert 'name' in response.json()
    assert IncomeSource.objects.count() == 0


def test_create_duplicate_name_ignores_case(admin, income_source):
    response = client_for(admin).post(LIST_URL, {'name': 'BONUS'}, format='json')

    assert response.status_code == 400
    assert response.json()['name'] == ['Există deja o sursă de venit cu acest nume în gospodărie.']
    assert IncomeSource.objects.count() == 1


def test_same_name_allowed_in_another_household(other_admin, income_source):
    response = client_for(other_admin).post(LIST_URL, {'name': 'Bonus'}, format='json')

    assert response.status_code == 201
    assert other_admin.household.income_sources.count() == 1


def test_create_ignores_household_sent_by_client(admin, other_admin):
    response = client_for(admin).post(
        LIST_URL, {'name': 'Bonus', 'household': str(other_admin.household.id)}, format='json'
    )

    assert response.status_code == 201
    assert IncomeSource.objects.get().household == admin.household


def test_member_cannot_create(member):
    response = client_for(member).post(LIST_URL, {'name': 'Bonus'}, format='json')

    assert response.status_code == 403
    assert response.json()['detail'] == 'Doar administratorul gospodăriei poate face modificări.'
    assert IncomeSource.objects.count() == 0


def test_create_requires_csrf(admin):
    client = APIClient(enforce_csrf_checks=True)
    client.force_login(admin)

    response = client.post(LIST_URL, {'name': 'Bonus'}, format='json')

    assert response.status_code == 403
    assert IncomeSource.objects.count() == 0


# Editare


def test_deactivate_income_source(admin, income_source, csrf_client):
    csrf_client.force_login(admin)

    response = csrf_client.patch(detail_url(income_source.id), {'is_active': False}, format='json')

    assert response.status_code == 200
    assert response.json() == {'id': str(income_source.id), 'name': 'Bonus', 'is_active': False}
    income_source.refresh_from_db()
    assert income_source.is_active is False
    assert income_source.name == 'Bonus'


def test_rename_income_source(admin, income_source):
    response = client_for(admin).patch(
        detail_url(income_source.id), {'name': 'Prime'}, format='json'
    )

    assert response.status_code == 200
    income_source.refresh_from_db()
    assert income_source.name == 'Prime'
    assert income_source.is_active is True


def test_rename_keeping_own_name_is_allowed(admin, income_source):
    response = client_for(admin).patch(
        detail_url(income_source.id), {'name': 'BONUS'}, format='json'
    )

    assert response.status_code == 200
    income_source.refresh_from_db()
    assert income_source.name == 'BONUS'


def test_rename_to_existing_name_returns_400(admin, income_source):
    IncomeSource.objects.create(household=admin.household, name='Salariu')

    response = client_for(admin).patch(
        detail_url(income_source.id), {'name': 'salariu'}, format='json'
    )

    assert response.status_code == 400
    assert 'name' in response.json()
    income_source.refresh_from_db()
    assert income_source.name == 'Bonus'


def test_other_household_cannot_edit(other_admin, income_source):
    response = client_for(other_admin).patch(
        detail_url(income_source.id), {'is_active': False}, format='json'
    )

    assert response.status_code == 404
    income_source.refresh_from_db()
    assert income_source.is_active is True


def test_member_cannot_edit(member, income_source):
    response = client_for(member).patch(
        detail_url(income_source.id), {'is_active': False}, format='json'
    )

    assert response.status_code == 403
    income_source.refresh_from_db()
    assert income_source.is_active is True


def test_edit_requires_csrf(admin, income_source):
    client = APIClient(enforce_csrf_checks=True)
    client.force_login(admin)

    response = client.patch(detail_url(income_source.id), {'is_active': False}, format='json')

    assert response.status_code == 403
    income_source.refresh_from_db()
    assert income_source.is_active is True


def test_edit_invalid_id_returns_404(admin):
    response = client_for(admin).patch('/api/v1/income-sources/abc/', {}, format='json')

    assert response.status_code == 404


# Operații care nu există


def test_delete_not_allowed(admin, income_source):
    response = client_for(admin).delete(detail_url(income_source.id))

    assert response.status_code == 405
    assert IncomeSource.objects.filter(pk=income_source.pk).exists()


def test_put_not_allowed(admin, income_source):
    response = client_for(admin).put(
        detail_url(income_source.id), {'name': 'X', 'is_active': True}, format='json'
    )

    assert response.status_code == 405
