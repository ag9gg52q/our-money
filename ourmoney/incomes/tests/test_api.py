import datetime
from decimal import Decimal

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from households.services import create_household, join_household
from income_sources.models import IncomeSource
from incomes.models import Income
from users.models import User

pytestmark = pytest.mark.django_db
LIST_URL = reverse('income-list')


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
def salary(admin):
    return IncomeSource.objects.create(household=admin.household, name='Salariu')


@pytest.fixture
def bonus(admin):
    return IncomeSource.objects.create(household=admin.household, name='Bonus')


@pytest.fixture
def other_source(other_admin):
    return IncomeSource.objects.create(household=other_admin.household, name='Salariu')


def client_for(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


def make_income(person, income_source, **fields):
    data = {
        'household': person.household,
        'date': datetime.date(2026, 11, 5),
        'person': person,
        'income_source': income_source,
        'amount': Decimal('5000.00'),
    }
    data.update(fields)
    return Income.objects.create(**data)


def payload(person, income_source, /, **fields):
    data = {
        'date': '2026-11-05',
        'person': str(person.id),
        'income_source': str(income_source.id),
        'amount': '5000.00',
        'note': 'Salariu noiembrie',
    }
    data.update(fields)
    return data


def notes(response):
    return [i['note'] for i in response.json()['incomes']]


# Listare


def test_list_response_format(admin, salary):
    income = make_income(admin, salary, note='Noiembrie')

    response = client_for(admin).get(LIST_URL)

    assert response.status_code == 200
    assert response.json() == {
        'incomes': [
            {
                'id': str(income.id),
                'date': '2026-11-05',
                'amount': '5000.00',
                'note': 'Noiembrie',
                'person': str(admin.id),
                'person_name': 'admin',
                'income_source': str(salary.id),
                'income_source_name': 'Salariu',
            }
        ],
        'total': '5000.00',
    }


def test_list_is_ordered_newest_first(admin, salary):
    make_income(admin, salary, date=datetime.date(2026, 11, 1), note='vechi')
    make_income(admin, salary, date=datetime.date(2026, 11, 3), note='nou')

    response = client_for(admin).get(LIST_URL)

    assert notes(response) == ['nou', 'vechi']


def test_member_sees_all_household_incomes(admin, member, salary):
    make_income(admin, salary, note='al adminului')
    make_income(member, salary, note='al membrului')

    response = client_for(member).get(LIST_URL)

    assert response.status_code == 200
    assert set(notes(response)) == {'al adminului', 'al membrului'}


def test_list_hides_other_household_incomes(other_admin, admin, salary):
    make_income(admin, salary)

    response = client_for(other_admin).get(LIST_URL)

    assert response.status_code == 200
    assert response.json() == {'incomes': [], 'total': '0.00'}


def test_list_keeps_incomes_with_deactivated_source(admin, salary):
    make_income(admin, salary)
    salary.is_active = False
    salary.save()

    response = client_for(admin).get(LIST_URL)

    assert len(response.json()['incomes']) == 1


def test_list_query_count_does_not_grow_with_incomes(admin, salary, django_assert_max_num_queries):
    for _ in range(5):
        make_income(admin, salary)
    client = client_for(admin)

    # O cerere pentru listă (cu JOIN-uri) și una pentru total.
    with django_assert_max_num_queries(2):
        response = client.get(LIST_URL)

    assert len(response.json()['incomes']) == 5


def test_list_without_household_returns_403(user):
    response = client_for(user).get(LIST_URL)

    assert response.status_code == 403


def test_list_unauthenticated_returns_403(api_client):
    response = api_client.get(LIST_URL)

    assert response.status_code == 403


# Adăugare


def test_member_can_create_income(member, salary, csrf_client):
    csrf_client.force_login(member)

    response = csrf_client.post(LIST_URL, payload(member, salary), format='json')

    assert response.status_code == 201
    income = Income.objects.get()
    assert income.household == member.household
    assert income.person == member
    assert income.income_source == salary
    assert income.amount == Decimal('5000.00')
    assert response.json()['id'] == str(income.id)
    assert response.json()['income_source_name'] == 'Salariu'


def test_create_for_another_member_of_household(admin, member, salary):
    response = client_for(admin).post(LIST_URL, payload(member, salary), format='json')

    assert response.status_code == 201
    assert Income.objects.get().person == member


def test_create_ignores_household_sent_by_client(admin, other_admin, salary):
    data = payload(admin, salary, household=str(other_admin.household_id))

    response = client_for(admin).post(LIST_URL, data, format='json')

    assert response.status_code == 201
    assert Income.objects.get().household == admin.household


def test_create_note_is_optional(admin, salary):
    data = payload(admin, salary)
    del data['note']

    response = client_for(admin).post(LIST_URL, data, format='json')

    assert response.status_code == 201
    assert Income.objects.get().note == ''


def test_create_note_too_long_returns_400(admin, salary):
    response = client_for(admin).post(
        LIST_URL, payload(admin, salary, note='x' * 256), format='json'
    )

    assert response.status_code == 400
    assert 'note' in response.json()


@pytest.mark.parametrize('field', ['date', 'person', 'income_source', 'amount'])
def test_create_without_required_field_returns_400(admin, salary, field):
    data = payload(admin, salary)
    del data[field]

    response = client_for(admin).post(LIST_URL, data, format='json')

    assert response.status_code == 400
    assert response.json()[field] == ['Acest câmp nu poate fi gol.']
    assert Income.objects.count() == 0


@pytest.mark.parametrize('field', ['date', 'person', 'income_source', 'amount'])
@pytest.mark.parametrize('value', ['', None])
def test_create_with_empty_required_field_returns_400(admin, salary, field, value):
    data = payload(admin, salary, **{field: value})

    response = client_for(admin).post(LIST_URL, data, format='json')

    assert response.status_code == 400
    assert response.json()[field] == ['Acest câmp nu poate fi gol.']
    assert Income.objects.count() == 0


@pytest.mark.parametrize('amount', ['0', '0.00', '-5', '12.345', 'abc'])
def test_create_invalid_amount_returns_400(admin, salary, amount):
    response = client_for(admin).post(
        LIST_URL, payload(admin, salary, amount=amount), format='json'
    )

    assert response.status_code == 400
    assert 'amount' in response.json()
    assert Income.objects.count() == 0


def test_create_with_person_from_other_household_returns_400(admin, other_admin, salary):
    response = client_for(admin).post(
        LIST_URL, payload(admin, salary, person=str(other_admin.id)), format='json'
    )

    assert response.status_code == 400
    assert 'person' in response.json()


def test_create_with_source_from_other_household_returns_400(admin, salary, other_source):
    response = client_for(admin).post(
        LIST_URL, payload(admin, salary, income_source=str(other_source.id)), format='json'
    )

    assert response.status_code == 400
    assert 'income_source' in response.json()


def test_create_with_deactivated_source_returns_400(admin, salary):
    salary.is_active = False
    salary.save()

    response = client_for(admin).post(LIST_URL, payload(admin, salary), format='json')

    assert response.status_code == 400
    assert 'income_source' in response.json()


def test_create_without_household_returns_403(user, admin, salary):
    response = client_for(user).post(LIST_URL, payload(admin, salary), format='json')

    assert response.status_code == 403
    assert Income.objects.count() == 0


def test_create_requires_csrf(admin, salary):
    client = APIClient(enforce_csrf_checks=True)
    client.force_login(admin)

    response = client.post(LIST_URL, payload(admin, salary), format='json')

    assert response.status_code == 403
    assert Income.objects.count() == 0


# Filtre și total


@pytest.fixture
def november(admin, member, salary, bonus):
    make_income(admin, salary, date=datetime.date(2026, 10, 31), note='octombrie')
    make_income(admin, salary, date=datetime.date(2026, 11, 1), note='1 nov')
    make_income(
        member,
        bonus,
        date=datetime.date(2026, 11, 15),
        amount=Decimal('250.50'),
        note='bonus',
    )
    make_income(admin, salary, date=datetime.date(2026, 11, 30), note='30 nov')
    make_income(admin, salary, date=datetime.date(2026, 12, 1), note='decembrie')


def test_total_is_sum_of_listed_incomes(admin, november):
    response = client_for(admin).get(LIST_URL)

    assert response.json()['total'] == '20250.50'


def test_filter_by_period_includes_both_ends(admin, november):
    response = client_for(admin).get(LIST_URL, {'date_from': '2026-11-01', 'date_to': '2026-11-30'})

    assert response.status_code == 200
    assert notes(response) == ['30 nov', 'bonus', '1 nov']
    assert response.json()['total'] == '10250.50'


def test_filter_by_date_from_only(admin, november):
    response = client_for(admin).get(LIST_URL, {'date_from': '2026-11-30'})

    assert notes(response) == ['decembrie', '30 nov']


def test_filter_by_date_to_only(admin, november):
    response = client_for(admin).get(LIST_URL, {'date_to': '2026-10-31'})

    assert notes(response) == ['octombrie']


def test_filter_by_person(admin, member, november):
    response = client_for(admin).get(LIST_URL, {'person': str(member.id)})

    assert notes(response) == ['bonus']
    assert response.json()['total'] == '250.50'


def test_filters_are_combined(admin, november):
    response = client_for(admin).get(
        LIST_URL,
        {'date_from': '2026-11-01', 'date_to': '2026-11-30', 'person': str(admin.id)},
    )

    assert notes(response) == ['30 nov', '1 nov']
    assert response.json()['total'] == '10000.00'


def test_filter_without_results_returns_zero_total(admin, november):
    response = client_for(admin).get(LIST_URL, {'date_from': '2027-01-01'})

    assert response.json() == {'incomes': [], 'total': '0.00'}


def test_filter_by_other_household_person_returns_nothing(admin, other_admin, november):
    response = client_for(admin).get(LIST_URL, {'person': str(other_admin.id)})

    assert response.status_code == 200
    assert response.json() == {'incomes': [], 'total': '0.00'}


def test_date_to_before_date_from_returns_400(admin):
    response = client_for(admin).get(LIST_URL, {'date_from': '2026-11-30', 'date_to': '2026-11-01'})

    assert response.status_code == 400
    assert response.json() == {
        'date_to': ['Data de sfârșit nu poate fi înainte de data de început.']
    }


@pytest.mark.parametrize(
    'params',
    [
        {'date_from': 'abc'},
        {'date_to': '2026-13-01'},
        {'person': 'x'},
    ],
)
def test_invalid_filter_returns_400(admin, params):
    response = client_for(admin).get(LIST_URL, params)

    assert response.status_code == 400
    assert set(response.json()) == set(params)


# Editare


def detail_url(income_id):
    return reverse('income-detail', args=[income_id])


@pytest.fixture
def income(admin, salary):
    return make_income(admin, salary, note='Noiembrie')


def test_member_can_edit_admin_income(member, income, csrf_client):
    csrf_client.force_login(member)

    response = csrf_client.patch(detail_url(income.id), {'amount': '5200.00'}, format='json')

    assert response.status_code == 200
    assert response.json()['amount'] == '5200.00'
    assert response.json()['note'] == 'Noiembrie'
    income.refresh_from_db()
    assert income.amount == Decimal('5200.00')
    assert income.note == 'Noiembrie'


def test_edit_income_source(admin, income, bonus):
    response = client_for(admin).patch(
        detail_url(income.id), {'income_source': str(bonus.id)}, format='json'
    )

    assert response.status_code == 200
    assert response.json()['income_source_name'] == 'Bonus'
    income.refresh_from_db()
    assert income.income_source == bonus


def test_edit_updates_updated_at(admin, income):
    before = income.updated_at

    client_for(admin).patch(detail_url(income.id), {'note': 'Decembrie'}, format='json')

    income.refresh_from_db()
    assert income.updated_at > before


def test_edit_keeps_current_deactivated_source(admin, income, salary):
    salary.is_active = False
    salary.save()
    data = payload(admin, salary, amount='5100.00')

    response = client_for(admin).patch(detail_url(income.id), data, format='json')

    assert response.status_code == 200
    income.refresh_from_db()
    assert income.amount == Decimal('5100.00')


def test_edit_cannot_move_to_deactivated_source(admin, income, bonus):
    bonus.is_active = False
    bonus.save()

    response = client_for(admin).patch(
        detail_url(income.id), {'income_source': str(bonus.id)}, format='json'
    )

    assert response.status_code == 400
    assert 'income_source' in response.json()


def test_edit_cannot_set_source_from_other_household(admin, income, other_source):
    response = client_for(admin).patch(
        detail_url(income.id), {'income_source': str(other_source.id)}, format='json'
    )

    assert response.status_code == 400
    assert 'income_source' in response.json()


def test_edit_keeps_person_who_left_household(admin, member, salary):
    income = make_income(member, salary)
    member.household = None
    member.save()

    response = client_for(admin).patch(
        detail_url(income.id), {'person': str(member.id), 'amount': '5.00'}, format='json'
    )

    assert response.status_code == 200


def test_edit_cannot_set_person_from_other_household(admin, other_admin, income):
    response = client_for(admin).patch(
        detail_url(income.id), {'person': str(other_admin.id)}, format='json'
    )

    assert response.status_code == 400
    assert 'person' in response.json()


def test_edit_invalid_amount_returns_400(admin, income):
    response = client_for(admin).patch(detail_url(income.id), {'amount': '0'}, format='json')

    assert response.status_code == 400
    assert 'amount' in response.json()


def test_edit_with_empty_field_returns_400(admin, income):
    response = client_for(admin).patch(detail_url(income.id), {'amount': ''}, format='json')

    assert response.status_code == 400
    assert response.json() == {'amount': ['Acest câmp nu poate fi gol.']}


def test_other_household_cannot_edit(other_admin, income):
    response = client_for(other_admin).patch(
        detail_url(income.id), {'amount': '1.00'}, format='json'
    )

    assert response.status_code == 404
    income.refresh_from_db()
    assert income.amount == Decimal('5000.00')


def test_edit_unknown_id_returns_404(admin):
    response = client_for(admin).patch(
        detail_url('00000000-0000-0000-0000-000000000000'), {'amount': '1.00'}, format='json'
    )

    assert response.status_code == 404


def test_edit_requires_csrf(admin, income):
    client = APIClient(enforce_csrf_checks=True)
    client.force_login(admin)

    response = client.patch(detail_url(income.id), {'amount': '1.00'}, format='json')

    assert response.status_code == 403


def test_put_not_allowed(admin, income):
    response = client_for(admin).put(detail_url(income.id), {}, format='json')

    assert response.status_code == 405


# Ștergere


def test_member_can_delete_income(member, income, csrf_client):
    csrf_client.force_login(member)

    response = csrf_client.delete(detail_url(income.id))

    assert response.status_code == 204
    assert Income.objects.count() == 0


def test_other_household_cannot_delete(other_admin, income):
    response = client_for(other_admin).delete(detail_url(income.id))

    assert response.status_code == 404
    assert Income.objects.count() == 1


def test_delete_without_household_returns_403(user, income):
    response = client_for(user).delete(detail_url(income.id))

    assert response.status_code == 403
    assert Income.objects.count() == 1


def test_delete_requires_csrf(admin, income):
    client = APIClient(enforce_csrf_checks=True)
    client.force_login(admin)

    response = client.delete(detail_url(income.id))

    assert response.status_code == 403
    assert Income.objects.count() == 1
