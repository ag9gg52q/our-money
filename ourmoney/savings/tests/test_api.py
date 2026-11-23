import datetime
from decimal import Decimal

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from households.services import create_household, join_household
from savings.models import SavingsEntry
from savings.services import NEGATIVE_BALANCE_MESSAGE
from users.models import User

pytestmark = pytest.mark.django_db
LIST_URL = reverse('savings-entry-list')


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


def client_for(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


def make_entry(person, **fields):
    data = {
        'household': person.household,
        'date': datetime.date(2026, 11, 5),
        'person': person,
        'amount': Decimal('1000.00'),
    }
    data.update(fields)
    return SavingsEntry.objects.create(**data)


def payload(person, /, **fields):
    data = {
        'date': '2026-11-05',
        'person': str(person.id),
        'amount': '1000.00',
        'note': 'Depunere lunară',
    }
    data.update(fields)
    return data


def detail_url(entry_id):
    return reverse('savings-entry-detail', args=[entry_id])


def notes(response):
    return [e['note'] for e in response.json()['savings_entries']]


# Permisiuni: totul e doar pentru administratorul gospodăriei


def test_unauthenticated_returns_403(api_client):
    response = api_client.get(LIST_URL)

    assert response.status_code == 403


def test_without_household_returns_403(user):
    response = client_for(user).get(LIST_URL)

    assert response.status_code == 403
    assert response.json() == {'detail': 'Nu faci parte dintr-o gospodărie.'}


def test_member_cannot_list(member):
    response = client_for(member).get(LIST_URL)

    assert response.status_code == 403
    assert response.json() == {
        'detail': 'Doar administratorul gospodăriei poate accesa acest compartiment.'
    }


def test_member_cannot_create(member):
    response = client_for(member).post(LIST_URL, payload(member), format='json')

    assert response.status_code == 403
    assert SavingsEntry.objects.count() == 0


def test_member_cannot_edit(admin, member):
    entry = make_entry(admin)

    response = client_for(member).patch(detail_url(entry.id), {'note': 'x'}, format='json')

    assert response.status_code == 403


def test_member_cannot_delete(admin, member):
    entry = make_entry(admin)

    response = client_for(member).delete(detail_url(entry.id))

    assert response.status_code == 403
    assert SavingsEntry.objects.count() == 1


# Listare și sumar


def test_list_response_format(admin):
    entry = make_entry(admin, note='Noiembrie')

    response = client_for(admin).get(LIST_URL)

    assert response.status_code == 200
    assert response.json() == {
        'savings_entries': [
            {
                'id': str(entry.id),
                'date': '2026-11-05',
                'amount': '1000.00',
                'note': 'Noiembrie',
                'person': str(admin.id),
                'person_name': 'admin',
            }
        ],
        'balance': '1000.00',
        'deposits': '1000.00',
        'withdrawals': '0.00',
    }


def test_empty_list_has_zero_summary(admin):
    response = client_for(admin).get(LIST_URL)

    assert response.json() == {
        'savings_entries': [],
        'balance': '0.00',
        'deposits': '0.00',
        'withdrawals': '0.00',
    }


def test_summary_separates_deposits_and_withdrawals(admin, member):
    make_entry(admin, amount=Decimal('1000.00'))
    make_entry(member, amount=Decimal('2000.00'))
    make_entry(admin, amount=Decimal('-500.00'))

    response = client_for(admin).get(LIST_URL)

    data = response.json()
    assert (data['balance'], data['deposits'], data['withdrawals']) == (
        '2500.00',
        '3000.00',
        '-500.00',
    )


def test_list_is_ordered_newest_first(admin):
    make_entry(admin, date=datetime.date(2026, 11, 1), note='vechi')
    make_entry(admin, date=datetime.date(2026, 11, 3), note='nou')

    response = client_for(admin).get(LIST_URL)

    assert notes(response) == ['nou', 'vechi']


def test_list_hides_other_household_entries(admin, other_admin):
    make_entry(admin)

    response = client_for(other_admin).get(LIST_URL)

    assert response.json()['savings_entries'] == []
    assert response.json()['balance'] == '0.00'


def test_list_query_count_does_not_grow_with_entries(admin, django_assert_max_num_queries):
    for _ in range(5):
        make_entry(admin)
    client = client_for(admin)

    # O cerere pentru listă (cu JOIN pe persoană) și una pentru sumar.
    with django_assert_max_num_queries(2):
        response = client.get(LIST_URL)

    assert len(response.json()['savings_entries']) == 5


# Adăugare


def test_admin_can_create_deposit(admin, csrf_client):
    csrf_client.force_login(admin)

    response = csrf_client.post(LIST_URL, payload(admin), format='json')

    assert response.status_code == 201
    entry = SavingsEntry.objects.get()
    assert entry.household == admin.household
    assert entry.amount == Decimal('1000.00')
    assert response.json()['id'] == str(entry.id)


def test_create_withdrawal_within_balance(admin):
    make_entry(admin, amount=Decimal('1000.00'))

    response = client_for(admin).post(LIST_URL, payload(admin, amount='-800.00'), format='json')

    assert response.status_code == 201
    assert response.json()['amount'] == '-800.00'


def test_create_withdrawal_of_whole_balance(admin):
    make_entry(admin, amount=Decimal('1000.00'))

    response = client_for(admin).post(LIST_URL, payload(admin, amount='-1000.00'), format='json')

    assert response.status_code == 201


def test_create_withdrawal_over_balance_returns_400(admin):
    make_entry(admin, amount=Decimal('1000.00'))

    response = client_for(admin).post(LIST_URL, payload(admin, amount='-1000.01'), format='json')

    assert response.status_code == 400
    assert response.json() == {'amount': [NEGATIVE_BALANCE_MESSAGE]}
    assert SavingsEntry.objects.count() == 1


def test_create_for_another_member_of_household(admin, member):
    response = client_for(admin).post(LIST_URL, payload(member), format='json')

    assert response.status_code == 201
    assert SavingsEntry.objects.get().person == member


def test_create_ignores_household_sent_by_client(admin, other_admin):
    data = payload(admin, household=str(other_admin.household_id))

    response = client_for(admin).post(LIST_URL, data, format='json')

    assert response.status_code == 201
    assert SavingsEntry.objects.get().household == admin.household


def test_create_note_is_optional(admin):
    data = payload(admin)
    del data['note']

    response = client_for(admin).post(LIST_URL, data, format='json')

    assert response.status_code == 201
    assert SavingsEntry.objects.get().note == ''


@pytest.mark.parametrize('field', ['date', 'person', 'amount'])
@pytest.mark.parametrize('value', ['', None])
def test_create_with_empty_required_field_returns_400(admin, field, value):
    response = client_for(admin).post(LIST_URL, payload(admin, **{field: value}), format='json')

    assert response.status_code == 400
    assert response.json() == {field: ['Acest câmp nu poate fi gol.']}


@pytest.mark.parametrize('field', ['date', 'person', 'amount'])
def test_create_without_required_field_returns_400(admin, field):
    data = payload(admin)
    del data[field]

    response = client_for(admin).post(LIST_URL, data, format='json')

    assert response.status_code == 400
    assert response.json() == {field: ['Acest câmp nu poate fi gol.']}


@pytest.mark.parametrize('amount', ['0', '0.00', '-0.00'])
def test_create_zero_amount_returns_400(admin, amount):
    response = client_for(admin).post(LIST_URL, payload(admin, amount=amount), format='json')

    assert response.status_code == 400
    assert response.json() == {'amount': ['Suma trebuie să fie diferită de zero.']}


@pytest.mark.parametrize('amount', ['12.345', 'abc'])
def test_create_invalid_amount_returns_400(admin, amount):
    response = client_for(admin).post(LIST_URL, payload(admin, amount=amount), format='json')

    assert response.status_code == 400
    assert 'amount' in response.json()


def test_create_with_person_from_other_household_returns_400(admin, other_admin):
    response = client_for(admin).post(LIST_URL, payload(other_admin), format='json')

    assert response.status_code == 400
    assert 'person' in response.json()


def test_create_requires_csrf(admin):
    client = APIClient(enforce_csrf_checks=True)
    client.force_login(admin)

    response = client.post(LIST_URL, payload(admin), format='json')

    assert response.status_code == 403
    assert SavingsEntry.objects.count() == 0


# Editare


@pytest.fixture
def deposit(admin):
    return make_entry(admin, amount=Decimal('1000.00'), note='Depunere')


@pytest.fixture
def withdrawal(admin, deposit):
    return make_entry(admin, amount=Decimal('-800.00'), note='Retragere')


def test_edit_note_only(admin, deposit, withdrawal):
    response = client_for(admin).patch(detail_url(deposit.id), {'note': 'Bonus'}, format='json')

    assert response.status_code == 200
    assert response.json()['note'] == 'Bonus'
    assert response.json()['amount'] == '1000.00'


def test_edit_amount_within_balance(admin, deposit, withdrawal):
    # Sold 200: depunerea poate scădea cu cel mult 200.
    response = client_for(admin).patch(detail_url(deposit.id), {'amount': '800.00'}, format='json')

    assert response.status_code == 200
    deposit.refresh_from_db()
    assert deposit.amount == Decimal('800.00')


def test_edit_amount_making_balance_negative_returns_400(admin, deposit, withdrawal):
    response = client_for(admin).patch(detail_url(deposit.id), {'amount': '500.00'}, format='json')

    assert response.status_code == 400
    assert response.json() == {'amount': [NEGATIVE_BALANCE_MESSAGE]}
    deposit.refresh_from_db()
    assert deposit.amount == Decimal('1000.00')


def test_edit_deposit_into_withdrawal_returns_400(admin, deposit):
    response = client_for(admin).patch(detail_url(deposit.id), {'amount': '-100.00'}, format='json')

    assert response.status_code == 400
    assert response.json() == {'amount': [NEGATIVE_BALANCE_MESSAGE]}


def test_edit_zero_amount_returns_400(admin, deposit):
    response = client_for(admin).patch(detail_url(deposit.id), {'amount': '0'}, format='json')

    assert response.status_code == 400
    assert response.json() == {'amount': ['Suma trebuie să fie diferită de zero.']}


def test_edit_updates_updated_at(admin, deposit):
    before = deposit.updated_at

    client_for(admin).patch(detail_url(deposit.id), {'note': 'Bonus'}, format='json')

    deposit.refresh_from_db()
    assert deposit.updated_at > before


def test_edit_keeps_person_who_left_household(admin, member):
    entry = make_entry(member)
    member.household = None
    member.save()

    response = client_for(admin).patch(
        detail_url(entry.id), {'person': str(member.id), 'note': 'x'}, format='json'
    )

    assert response.status_code == 200


def test_edit_cannot_set_person_from_other_household(admin, other_admin, deposit):
    response = client_for(admin).patch(
        detail_url(deposit.id), {'person': str(other_admin.id)}, format='json'
    )

    assert response.status_code == 400
    assert 'person' in response.json()


def test_other_household_cannot_edit(other_admin, deposit):
    response = client_for(other_admin).patch(
        detail_url(deposit.id), {'amount': '1.00'}, format='json'
    )

    assert response.status_code == 404


def test_edit_unknown_id_returns_404(admin):
    response = client_for(admin).patch(
        detail_url('00000000-0000-0000-0000-000000000000'), {'note': 'x'}, format='json'
    )

    assert response.status_code == 404


def test_edit_requires_csrf(admin, deposit):
    client = APIClient(enforce_csrf_checks=True)
    client.force_login(admin)

    response = client.patch(detail_url(deposit.id), {'note': 'x'}, format='json')

    assert response.status_code == 403


def test_put_not_allowed(admin, deposit):
    response = client_for(admin).put(detail_url(deposit.id), {}, format='json')

    assert response.status_code == 405


# Ștergere


def test_delete_withdrawal(admin, deposit, withdrawal):
    response = client_for(admin).delete(detail_url(withdrawal.id))

    assert response.status_code == 204
    assert list(SavingsEntry.objects.all()) == [deposit]


def test_delete_deposit_making_balance_negative_returns_400(admin, deposit, withdrawal):
    response = client_for(admin).delete(detail_url(deposit.id))

    assert response.status_code == 400
    assert response.json() == {'non_field_errors': [NEGATIVE_BALANCE_MESSAGE]}
    assert SavingsEntry.objects.count() == 2


def test_delete_deposit_when_balance_allows(admin, deposit):
    response = client_for(admin).delete(detail_url(deposit.id))

    assert response.status_code == 204
    assert SavingsEntry.objects.count() == 0


def test_other_household_cannot_delete(other_admin, deposit):
    response = client_for(other_admin).delete(detail_url(deposit.id))

    assert response.status_code == 404
    assert SavingsEntry.objects.count() == 1


def test_delete_requires_csrf(admin, deposit):
    client = APIClient(enforce_csrf_checks=True)
    client.force_login(admin)

    response = client.delete(detail_url(deposit.id))

    assert response.status_code == 403
    assert SavingsEntry.objects.count() == 1
