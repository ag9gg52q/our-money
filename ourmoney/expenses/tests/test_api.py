import datetime
from decimal import Decimal

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from categories.models import Category
from expenses import services
from expenses.models import DUPLICATE_OPEN_DEBT, Expense, ExpenseDebt
from households.services import create_household, join_household
from subcategories.models import Subcategory
from users.models import User

pytestmark = pytest.mark.django_db
LIST_URL = reverse('expense-list')


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


@pytest.fixture
def other_subcategory(other_admin):
    other_category = Category.objects.create(household=other_admin.household, name='Alimente')
    return Subcategory.objects.create(category=other_category, name='Lactate')


def client_for(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


def make_expense(person, subcategory, **fields):
    data = {
        'household': person.household,
        'date': datetime.date(2026, 11, 5),
        'person': person,
        'category': subcategory.category,
        'subcategory': subcategory,
        'amount': Decimal('12.50'),
        'store': 'Kaufland',
    }
    data.update(fields)
    return Expense.objects.create(**data)


def payload(person, subcategory, /, **fields):
    data = {
        'date': '2026-11-05',
        'person': str(person.id),
        'category': str(subcategory.category_id),
        'subcategory': str(subcategory.id),
        'amount': '12.50',
        'store': 'Kaufland',
        'note': 'Lapte și brânză',
    }
    data.update(fields)
    return data


def notes(response):
    return [e['note'] for e in response.json()['expenses']]


# Listare


def test_list_response_format(admin, subcategory):
    expense = make_expense(
        admin, subcategory, store='Kaufland', note='Lapte', link='https://bon.md/123'
    )
    debt = ExpenseDebt.objects.create(expense=expense, debtor_name='Ion', amount='5.00')

    response = client_for(admin).get(LIST_URL)

    assert response.status_code == 200
    assert response.json() == {
        'expenses': [
            {
                'id': str(expense.id),
                'date': '2026-11-05',
                'amount': '12.50',
                'store': 'Kaufland',
                'note': 'Lapte',
                'link': 'https://bon.md/123',
                'person': str(admin.id),
                'person_name': 'admin',
                'category': str(subcategory.category_id),
                'category_name': 'Alimente',
                'subcategory': str(subcategory.id),
                'subcategory_name': 'Lactate',
                'debts': [
                    {
                        'id': str(debt.id),
                        'debtor': None,
                        'debtor_name': 'Ion',
                        'debtor_label': 'Ion',
                        'amount': '5.00',
                        'status': 'open',
                        'settled_at': None,
                    }
                ],
            }
        ],
        'total': '12.50',
    }


def test_list_is_ordered_newest_first(admin, subcategory):
    make_expense(admin, subcategory, date=datetime.date(2026, 11, 1), note='veche')
    make_expense(admin, subcategory, date=datetime.date(2026, 11, 3), note='nouă')

    response = client_for(admin).get(LIST_URL)

    assert notes(response) == ['nouă', 'veche']


def test_member_sees_all_household_expenses(admin, member, subcategory):
    make_expense(admin, subcategory, note='a adminului')
    make_expense(member, subcategory, note='a membrului')

    response = client_for(member).get(LIST_URL)

    assert response.status_code == 200
    assert set(notes(response)) == {'a adminului', 'a membrului'}


def test_list_hides_other_household_expenses(other_admin, admin, subcategory):
    make_expense(admin, subcategory)

    response = client_for(other_admin).get(LIST_URL)

    assert response.status_code == 200
    assert response.json() == {'expenses': [], 'total': '0.00'}


def test_list_keeps_expenses_with_deactivated_category(admin, category, subcategory):
    make_expense(admin, subcategory)
    category.is_active = False
    category.save()

    response = client_for(admin).get(LIST_URL)

    assert len(response.json()['expenses']) == 1


def test_list_query_count_does_not_grow_with_expenses(
    admin, member, subcategory, django_assert_max_num_queries
):
    for _ in range(5):
        expense = make_expense(admin, subcategory)
        ExpenseDebt.objects.create(expense=expense, debtor=member, amount='1.00')
    client = client_for(admin)

    # Lista (cu JOIN-uri), datoriile tuturor cheltuielilor (cu datornicii) și totalul.
    with django_assert_max_num_queries(3):
        response = client.get(LIST_URL)

    assert len(response.json()['expenses']) == 5


def test_list_without_household_returns_403(user):
    response = client_for(user).get(LIST_URL)

    assert response.status_code == 403


def test_list_unauthenticated_returns_403(api_client):
    response = api_client.get(LIST_URL)

    assert response.status_code == 403


# Adăugare


def test_member_can_create_expense(member, subcategory, csrf_client):
    csrf_client.force_login(member)

    response = csrf_client.post(LIST_URL, payload(member, subcategory), format='json')

    assert response.status_code == 201
    expense = Expense.objects.get()
    assert expense.household == member.household
    assert expense.person == member
    assert expense.subcategory == subcategory
    assert expense.amount == Decimal('12.50')
    assert response.json()['id'] == str(expense.id)
    assert response.json()['category_name'] == 'Alimente'


def test_create_for_another_member_of_household(admin, member, subcategory):
    response = client_for(admin).post(LIST_URL, payload(member, subcategory), format='json')

    assert response.status_code == 201
    assert Expense.objects.get().person == member


def test_create_ignores_household_sent_by_client(admin, other_admin, subcategory):
    data = payload(admin, subcategory, household=str(other_admin.household_id))

    response = client_for(admin).post(LIST_URL, data, format='json')

    assert response.status_code == 201
    assert Expense.objects.get().household == admin.household


def test_create_note_is_optional(admin, subcategory):
    data = payload(admin, subcategory)
    del data['note']

    response = client_for(admin).post(LIST_URL, data, format='json')

    assert response.status_code == 201
    assert Expense.objects.get().note == ''


def test_create_saves_store(admin, subcategory):
    response = client_for(admin).post(LIST_URL, payload(admin, subcategory), format='json')

    assert response.status_code == 201
    assert response.json()['store'] == 'Kaufland'
    assert Expense.objects.get().store == 'Kaufland'


def test_create_store_with_only_spaces_returns_400(admin, subcategory):
    response = client_for(admin).post(
        LIST_URL, payload(admin, subcategory, store='   '), format='json'
    )

    assert response.status_code == 400
    assert response.json() == {'store': ['Acest câmp nu poate fi gol.']}


def test_create_store_too_long_returns_400(admin, subcategory):
    response = client_for(admin).post(
        LIST_URL, payload(admin, subcategory, store='x' * 101), format='json'
    )

    assert response.status_code == 400
    assert 'store' in response.json()


def test_create_saves_link(admin, subcategory):
    data = payload(admin, subcategory, link='https://bon.md/123?id=abc')

    response = client_for(admin).post(LIST_URL, data, format='json')

    assert response.status_code == 201
    assert response.json()['link'] == 'https://bon.md/123?id=abc'
    assert Expense.objects.get().link == 'https://bon.md/123?id=abc'


def test_create_link_is_optional(admin, subcategory):
    response = client_for(admin).post(LIST_URL, payload(admin, subcategory), format='json')

    assert response.status_code == 201
    assert Expense.objects.get().link == ''


def test_create_accepts_uppercase_scheme(admin, subcategory):
    data = payload(admin, subcategory, link='HTTPS://bon.md/123')

    response = client_for(admin).post(LIST_URL, data, format='json')

    assert response.status_code == 201


@pytest.mark.parametrize('link', ['javascript:alert(1)', 'ftp://bon.md/1', 'bon.md/1'])
def test_create_with_invalid_link_returns_400(admin, subcategory, link):
    response = client_for(admin).post(
        LIST_URL, payload(admin, subcategory, link=link), format='json'
    )

    assert response.status_code == 400
    assert 'link' in response.json()
    assert not Expense.objects.exists()


def test_create_with_ftp_link_explains_allowed_schemes(admin, subcategory):
    response = client_for(admin).post(
        LIST_URL, payload(admin, subcategory, link='ftp://bon.md/1'), format='json'
    )

    assert response.json() == {'link': ['Linkul trebuie să înceapă cu http:// sau https://.']}


def test_create_link_too_long_returns_400(admin, subcategory):
    data = payload(admin, subcategory, link='https://bon.md/' + 'a' * 1000)

    response = client_for(admin).post(LIST_URL, data, format='json')

    assert response.status_code == 400
    assert 'link' in response.json()


@pytest.mark.parametrize('field', ['date', 'person', 'category', 'subcategory', 'amount', 'store'])
def test_create_without_required_field_returns_400(admin, subcategory, field):
    data = payload(admin, subcategory)
    del data[field]

    response = client_for(admin).post(LIST_URL, data, format='json')

    assert response.status_code == 400
    assert response.json()[field] == ['Acest câmp nu poate fi gol.']
    assert Expense.objects.count() == 0


@pytest.mark.parametrize('field', ['date', 'person', 'category', 'subcategory', 'amount', 'store'])
@pytest.mark.parametrize('value', ['', None])
def test_create_with_empty_required_field_returns_400(admin, subcategory, field, value):
    data = payload(admin, subcategory, **{field: value})

    response = client_for(admin).post(LIST_URL, data, format='json')

    assert response.status_code == 400
    assert response.json()[field] == ['Acest câmp nu poate fi gol.']
    assert Expense.objects.count() == 0


@pytest.mark.parametrize('amount', ['0', '0.00', '-5', '12.345', 'abc'])
def test_create_invalid_amount_returns_400(admin, subcategory, amount):
    response = client_for(admin).post(
        LIST_URL, payload(admin, subcategory, amount=amount), format='json'
    )

    assert response.status_code == 400
    assert 'amount' in response.json()
    assert Expense.objects.count() == 0


def test_create_with_person_from_other_household_returns_400(admin, other_admin, subcategory):
    response = client_for(admin).post(
        LIST_URL, payload(admin, subcategory, person=str(other_admin.id)), format='json'
    )

    assert response.status_code == 400
    assert 'person' in response.json()


def test_create_with_category_from_other_household_returns_400(admin, other_admin, subcategory):
    other_category = Category.objects.create(household=other_admin.household, name='Transport')

    response = client_for(admin).post(
        LIST_URL, payload(admin, subcategory, category=str(other_category.id)), format='json'
    )

    assert response.status_code == 400
    assert 'category' in response.json()


def test_create_with_subcategory_from_other_household_returns_400(
    admin, subcategory, other_subcategory
):
    response = client_for(admin).post(
        LIST_URL, payload(admin, subcategory, subcategory=str(other_subcategory.id)), format='json'
    )

    assert response.status_code == 400
    assert 'subcategory' in response.json()


def test_create_with_subcategory_of_another_category_returns_400(admin, subcategory):
    transport = Category.objects.create(household=admin.household, name='Transport')

    response = client_for(admin).post(
        LIST_URL, payload(admin, subcategory, category=str(transport.id)), format='json'
    )

    assert response.status_code == 400
    assert response.json() == {'subcategory': ['Subcategoria nu aparține categoriei alese.']}
    assert Expense.objects.count() == 0


def test_create_with_deactivated_category_returns_400(admin, category, subcategory):
    category.is_active = False
    category.save()

    response = client_for(admin).post(LIST_URL, payload(admin, subcategory), format='json')

    assert response.status_code == 400
    assert 'category' in response.json()


def test_create_with_deactivated_subcategory_returns_400(admin, subcategory):
    subcategory.is_active = False
    subcategory.save()

    response = client_for(admin).post(LIST_URL, payload(admin, subcategory), format='json')

    assert response.status_code == 400
    assert 'subcategory' in response.json()


def test_create_without_household_returns_403(user, admin, subcategory):
    response = client_for(user).post(LIST_URL, payload(admin, subcategory), format='json')

    assert response.status_code == 403
    assert Expense.objects.count() == 0


def test_create_requires_csrf(admin, subcategory):
    client = APIClient(enforce_csrf_checks=True)
    client.force_login(admin)

    response = client.post(LIST_URL, payload(admin, subcategory), format='json')

    assert response.status_code == 403
    assert Expense.objects.count() == 0


# Filtre și total


@pytest.fixture
def november(admin, subcategory, member, transport):
    benzina = transport.subcategories.get()
    make_expense(admin, subcategory, date=datetime.date(2026, 10, 31), note='octombrie')
    make_expense(admin, subcategory, date=datetime.date(2026, 11, 1), note='1 nov')
    make_expense(
        member,
        benzina,
        date=datetime.date(2026, 11, 15),
        amount=Decimal('100.25'),
        note='benzină',
    )
    make_expense(admin, subcategory, date=datetime.date(2026, 11, 30), note='30 nov')
    make_expense(admin, subcategory, date=datetime.date(2026, 12, 1), note='decembrie')


def test_total_is_sum_of_listed_expenses(admin, november):
    response = client_for(admin).get(LIST_URL)

    assert response.json()['total'] == '150.25'


def test_filter_by_period_includes_both_ends(admin, november):
    response = client_for(admin).get(LIST_URL, {'date_from': '2026-11-01', 'date_to': '2026-11-30'})

    assert response.status_code == 200
    assert notes(response) == ['30 nov', 'benzină', '1 nov']
    assert response.json()['total'] == '125.25'


def test_filter_by_date_from_only(admin, november):
    response = client_for(admin).get(LIST_URL, {'date_from': '2026-11-30'})

    assert notes(response) == ['decembrie', '30 nov']


def test_filter_by_date_to_only(admin, november):
    response = client_for(admin).get(LIST_URL, {'date_to': '2026-10-31'})

    assert notes(response) == ['octombrie']


def test_filter_by_category(admin, november, transport):
    response = client_for(admin).get(LIST_URL, {'category': str(transport.id)})

    assert notes(response) == ['benzină']
    assert response.json()['total'] == '100.25'


def test_filter_by_subcategory(admin, november, subcategory):
    response = client_for(admin).get(LIST_URL, {'subcategory': str(subcategory.id)})

    assert len(notes(response)) == 4
    assert 'benzină' not in notes(response)


def test_filter_by_person(admin, member, november):
    response = client_for(admin).get(LIST_URL, {'person': str(member.id)})

    assert notes(response) == ['benzină']


def test_filters_are_combined(admin, november, subcategory):
    response = client_for(admin).get(
        LIST_URL,
        {
            'date_from': '2026-11-01',
            'date_to': '2026-11-30',
            'subcategory': str(subcategory.id),
            'person': str(admin.id),
        },
    )

    assert notes(response) == ['30 nov', '1 nov']
    assert response.json()['total'] == '25.00'


def test_filter_without_results_returns_zero_total(admin, november):
    response = client_for(admin).get(LIST_URL, {'date_from': '2027-01-01'})

    assert response.json() == {'expenses': [], 'total': '0.00'}


def test_filter_by_other_household_category_returns_nothing(admin, other_subcategory, november):
    response = client_for(admin).get(LIST_URL, {'category': str(other_subcategory.category_id)})

    assert response.status_code == 200
    assert response.json() == {'expenses': [], 'total': '0.00'}


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
        {'category': 'nu-e-uuid'},
        {'subcategory': '123'},
        {'person': 'x'},
    ],
)
def test_invalid_filter_returns_400(admin, params):
    response = client_for(admin).get(LIST_URL, params)

    assert response.status_code == 400
    assert set(response.json()) == set(params)


# Editare


def detail_url(expense_id):
    return reverse('expense-detail', args=[expense_id])


@pytest.fixture
def expense(admin, subcategory):
    return make_expense(admin, subcategory, note='Lapte')


@pytest.fixture
def transport(admin):
    category = Category.objects.create(household=admin.household, name='Transport')
    Subcategory.objects.create(category=category, name='Benzină')
    return category


def test_member_can_edit_admin_expense(member, expense, csrf_client):
    csrf_client.force_login(member)

    response = csrf_client.patch(detail_url(expense.id), {'amount': '20.00'}, format='json')

    assert response.status_code == 200
    assert response.json()['amount'] == '20.00'
    assert response.json()['note'] == 'Lapte'
    expense.refresh_from_db()
    assert expense.amount == Decimal('20.00')
    assert expense.note == 'Lapte'


def test_edit_store(admin, expense):
    response = client_for(admin).patch(detail_url(expense.id), {'store': 'Lidl'}, format='json')

    assert response.status_code == 200
    expense.refresh_from_db()
    assert expense.store == 'Lidl'


def test_edit_can_clear_link(admin, subcategory):
    expense = make_expense(admin, subcategory, link='https://bon.md/123')

    response = client_for(admin).patch(detail_url(expense.id), {'link': ''}, format='json')

    assert response.status_code == 200
    expense.refresh_from_db()
    assert expense.link == ''


def test_edit_updates_updated_at(admin, expense):
    before = expense.updated_at

    client_for(admin).patch(detail_url(expense.id), {'note': 'Brânză'}, format='json')

    expense.refresh_from_db()
    assert expense.updated_at > before


def test_edit_category_and_subcategory_together(admin, expense, transport):
    benzina = transport.subcategories.get()

    response = client_for(admin).patch(
        detail_url(expense.id),
        {'category': str(transport.id), 'subcategory': str(benzina.id)},
        format='json',
    )

    assert response.status_code == 200
    assert response.json()['category_name'] == 'Transport'
    assert response.json()['subcategory_name'] == 'Benzină'


def test_edit_category_without_subcategory_returns_400(admin, expense, transport):
    response = client_for(admin).patch(
        detail_url(expense.id), {'category': str(transport.id)}, format='json'
    )

    assert response.status_code == 400
    assert response.json() == {'subcategory': ['Subcategoria nu aparține categoriei alese.']}
    expense.refresh_from_db()
    assert expense.category.name == 'Alimente'


def test_edit_keeps_current_deactivated_category(admin, expense, category, subcategory):
    category.is_active = False
    category.save()
    subcategory.is_active = False
    subcategory.save()
    data = payload(admin, subcategory, amount='30.00')

    response = client_for(admin).patch(detail_url(expense.id), data, format='json')

    assert response.status_code == 200
    expense.refresh_from_db()
    assert expense.amount == Decimal('30.00')


def test_edit_cannot_move_to_deactivated_category(admin, expense, transport):
    transport.is_active = False
    transport.save()
    benzina = transport.subcategories.get()

    response = client_for(admin).patch(
        detail_url(expense.id),
        {'category': str(transport.id), 'subcategory': str(benzina.id)},
        format='json',
    )

    assert response.status_code == 400
    assert 'category' in response.json()


def test_edit_keeps_person_who_left_household(admin, member, subcategory):
    expense = make_expense(member, subcategory)
    member.household = None
    member.save()

    response = client_for(admin).patch(
        detail_url(expense.id), {'person': str(member.id), 'amount': '5.00'}, format='json'
    )

    assert response.status_code == 200


def test_edit_cannot_set_person_from_other_household(admin, other_admin, expense):
    response = client_for(admin).patch(
        detail_url(expense.id), {'person': str(other_admin.id)}, format='json'
    )

    assert response.status_code == 400
    assert 'person' in response.json()


def test_edit_invalid_amount_returns_400(admin, expense):
    response = client_for(admin).patch(detail_url(expense.id), {'amount': '0'}, format='json')

    assert response.status_code == 400
    assert 'amount' in response.json()


def test_edit_with_empty_field_returns_400(admin, expense):
    response = client_for(admin).patch(detail_url(expense.id), {'amount': ''}, format='json')

    assert response.status_code == 400
    assert response.json() == {'amount': ['Acest câmp nu poate fi gol.']}


def test_other_household_cannot_edit(other_admin, expense):
    response = client_for(other_admin).patch(
        detail_url(expense.id), {'amount': '1.00'}, format='json'
    )

    assert response.status_code == 404
    expense.refresh_from_db()
    assert expense.amount == Decimal('12.50')


def test_edit_unknown_id_returns_404(admin):
    response = client_for(admin).patch(
        detail_url('00000000-0000-0000-0000-000000000000'), {'amount': '1.00'}, format='json'
    )

    assert response.status_code == 404


def test_edit_requires_csrf(admin, expense):
    client = APIClient(enforce_csrf_checks=True)
    client.force_login(admin)

    response = client.patch(detail_url(expense.id), {'amount': '1.00'}, format='json')

    assert response.status_code == 403


def test_put_not_allowed(admin, expense):
    response = client_for(admin).put(detail_url(expense.id), {}, format='json')

    assert response.status_code == 405


# Ștergere


def test_member_can_delete_expense(member, expense, csrf_client):
    csrf_client.force_login(member)

    response = csrf_client.delete(detail_url(expense.id))

    assert response.status_code == 204
    assert Expense.objects.count() == 0


def test_other_household_cannot_delete(other_admin, expense):
    response = client_for(other_admin).delete(detail_url(expense.id))

    assert response.status_code == 404
    assert Expense.objects.count() == 1


def test_delete_without_household_returns_403(user, expense):
    response = client_for(user).delete(detail_url(expense.id))

    assert response.status_code == 403
    assert Expense.objects.count() == 1


def test_delete_requires_csrf(admin, expense):
    client = APIClient(enforce_csrf_checks=True)
    client.force_login(admin)

    response = client.delete(detail_url(expense.id))

    assert response.status_code == 403
    assert Expense.objects.count() == 1


# Datorii la adăugare și editare


@pytest.fixture
def dinner(admin, subcategory):
    return make_expense(
        admin,
        subcategory,
        amount=Decimal('300.00'),
        store='La Plăcinte',
        note='Cină',
        link='https://bon.md/1',
    )


def make_debt(expense, amount='100.00', **debtor):
    return ExpenseDebt.objects.create(
        expense=expense, amount=Decimal(amount), **(debtor or {'debtor_name': 'Ion'})
    )


def close_debt(debt, status):
    debt.status = status
    debt.save()
    return debt


CLOSED_STATUSES = [ExpenseDebt.Status.SETTLED, ExpenseDebt.Status.CANCELED]


def test_create_with_member_and_external_debts(admin, member, subcategory):
    data = payload(
        admin,
        subcategory,
        amount='300.00',
        debts=[
            {'debtor': str(member.id), 'amount': '100.00'},
            {'debtor_name': 'Ion', 'amount': '50.00'},
        ],
    )

    response = client_for(admin).post(LIST_URL, data, format='json')

    assert response.status_code == 201
    debts = response.json()['debts']
    assert [(d['debtor_label'], d['amount'], d['status']) for d in debts] == [
        ('membru', '100.00', 'open'),
        ('Ion', '50.00', 'open'),
    ]
    expense = Expense.objects.get()
    assert expense.amount == Decimal('300.00')
    assert expense.debts.count() == 2


def test_create_without_debts_has_empty_list(admin, subcategory):
    response = client_for(admin).post(LIST_URL, payload(admin, subcategory), format='json')

    assert response.status_code == 201
    assert response.json()['debts'] == []


def test_create_debts_equal_to_amount_are_allowed(admin, subcategory):
    debts = [{'debtor_name': 'Ion', 'amount': '100.00'}]

    response = client_for(admin).post(
        LIST_URL, payload(admin, subcategory, amount='100.00', debts=debts), format='json'
    )

    assert response.status_code == 201


@pytest.mark.parametrize(
    'debt',
    [
        {'amount': '10.00'},
        {'debtor_name': '   ', 'amount': '10.00'},
        {'debtor': None, 'debtor_name': '', 'amount': '10.00'},
    ],
)
def test_create_debt_without_member_or_name_returns_400(admin, subcategory, debt):
    response = client_for(admin).post(
        LIST_URL, payload(admin, subcategory, debts=[debt]), format='json'
    )

    assert response.status_code == 400
    assert response.json()['debts']['0']['debtor'] == ['Alege un membru sau scrie un nume.']
    assert Expense.objects.count() == 0


def test_create_debt_with_member_and_name_returns_400(admin, member, subcategory):
    debt = {'debtor': str(member.id), 'debtor_name': 'Ion', 'amount': '10.00'}

    response = client_for(admin).post(
        LIST_URL, payload(admin, subcategory, debts=[debt]), format='json'
    )

    assert response.status_code == 400
    assert response.json()['debts']['0']['debtor'] == ['Alege un membru sau scrie un nume.']


def test_create_debt_with_member_of_other_household_returns_400(admin, other_admin, subcategory):
    debt = {'debtor': str(other_admin.id), 'amount': '10.00'}

    response = client_for(admin).post(
        LIST_URL, payload(admin, subcategory, debts=[debt]), format='json'
    )

    assert response.status_code == 400
    assert 'debtor' in response.json()['debts']['0']
    assert Expense.objects.count() == 0


@pytest.mark.parametrize('amount', ['0', '-5', '', 'abc'])
def test_create_debt_with_invalid_amount_returns_400(admin, subcategory, amount):
    debt = {'debtor_name': 'Ion', 'amount': amount}

    response = client_for(admin).post(
        LIST_URL, payload(admin, subcategory, debts=[debt]), format='json'
    )

    assert response.status_code == 400
    assert 'amount' in response.json()['debts']['0']


@pytest.mark.parametrize('names', [('Ion', 'Ion'), ('Ion', 'ion')])
def test_create_same_external_debtor_twice_returns_400(admin, subcategory, names):
    debts = [{'debtor_name': name, 'amount': '1.00'} for name in names]

    response = client_for(admin).post(
        LIST_URL, payload(admin, subcategory, debts=debts), format='json'
    )

    assert response.status_code == 400
    assert response.json() == {'debts': [DUPLICATE_OPEN_DEBT]}


def test_create_same_member_debtor_twice_returns_400(admin, member, subcategory):
    debts = [{'debtor': str(member.id), 'amount': '1.00'}] * 2

    response = client_for(admin).post(
        LIST_URL, payload(admin, subcategory, debts=debts), format='json'
    )

    assert response.status_code == 400
    assert response.json() == {'debts': [DUPLICATE_OPEN_DEBT]}


def test_create_debts_exceeding_amount_returns_400_and_saves_nothing(admin, member, subcategory):
    debts = [
        {'debtor': str(member.id), 'amount': '60.00'},
        {'debtor_name': 'Ion', 'amount': '40.01'},
    ]

    response = client_for(admin).post(
        LIST_URL, payload(admin, subcategory, amount='100.00', debts=debts), format='json'
    )

    assert response.status_code == 400
    assert response.json() == {'debts': [services.DEBTS_EXCEED_AMOUNT]}
    # Cheltuiala și datoriile fuseseră deja scrise; tranzacția le-a anulat.
    assert Expense.objects.count() == 0
    assert ExpenseDebt.objects.count() == 0


def test_create_debt_of_payer_returns_400(admin, subcategory):
    debt = {'debtor': str(admin.id), 'amount': '10.00'}

    response = client_for(admin).post(
        LIST_URL, payload(admin, subcategory, debts=[debt]), format='json'
    )

    assert response.status_code == 400
    assert response.json() == {'debts': [services.DEBTOR_IS_PAYER]}
    assert Expense.objects.count() == 0


def test_edit_updates_existing_debt_and_keeps_its_id(admin, dinner):
    debt = make_debt(dinner)
    debts = [{'id': str(debt.id), 'debtor_name': 'Ion Popa', 'amount': '80.00'}]

    response = client_for(admin).patch(detail_url(dinner.id), {'debts': debts}, format='json')

    assert response.status_code == 200
    assert [d['id'] for d in response.json()['debts']] == [str(debt.id)]
    debt.refresh_from_db()
    assert (debt.debtor_name, debt.amount) == ('Ion Popa', Decimal('80.00'))


def test_edit_adds_new_debt(admin, member, dinner):
    debt = make_debt(dinner)
    debts = [
        {'id': str(debt.id), 'debtor_name': 'Ion', 'amount': '100.00'},
        {'debtor': str(member.id), 'amount': '50.00'},
    ]

    response = client_for(admin).patch(detail_url(dinner.id), {'debts': debts}, format='json')

    assert response.status_code == 200
    assert dinner.debts.count() == 2


def test_edit_removes_debts_missing_from_list(admin, dinner):
    make_debt(dinner)

    response = client_for(admin).patch(detail_url(dinner.id), {'debts': []}, format='json')

    assert response.status_code == 200
    assert response.json()['debts'] == []
    assert ExpenseDebt.objects.count() == 0


def test_edit_without_debts_keeps_debts(admin, dinner):
    make_debt(dinner)

    response = client_for(admin).patch(detail_url(dinner.id), {'store': 'Andy'}, format='json')

    assert response.status_code == 200
    assert dinner.debts.count() == 1


def test_edit_can_replace_debt_of_same_person(admin, dinner):
    make_debt(dinner)
    debts = [{'debtor_name': 'ion', 'amount': '30.00'}]

    response = client_for(admin).patch(detail_url(dinner.id), {'debts': debts}, format='json')

    assert response.status_code == 200
    assert [(d.debtor_name, d.amount) for d in dinner.debts.all()] == [('ion', Decimal('30.00'))]


@pytest.mark.parametrize('status', CLOSED_STATUSES)
def test_edit_does_not_touch_closed_debts(admin, dinner, status):
    closed = close_debt(make_debt(dinner), status)

    response = client_for(admin).patch(detail_url(dinner.id), {'debts': []}, format='json')

    assert response.status_code == 200
    closed.refresh_from_db()
    assert closed.status == status
    # Răspunsul arată tot istoricul, nu doar datoriile deschise.
    assert [d['status'] for d in response.json()['debts']] == [status]


@pytest.mark.parametrize('status', CLOSED_STATUSES)
def test_edit_cannot_change_closed_debt(admin, dinner, status):
    closed = close_debt(make_debt(dinner), status)
    debts = [{'id': str(closed.id), 'debtor_name': 'Ion', 'amount': '1.00'}]

    response = client_for(admin).patch(detail_url(dinner.id), {'debts': debts}, format='json')

    assert response.status_code == 400
    assert response.json() == {'debts': [services.DEBT_NOT_FOUND]}
    closed.refresh_from_db()
    assert closed.amount == Decimal('100.00')


def test_edit_cannot_change_debt_of_other_expense(admin, subcategory, dinner):
    other_debt = make_debt(make_expense(admin, subcategory, amount=Decimal('500.00')))
    debts = [{'id': str(other_debt.id), 'debtor_name': 'Ion', 'amount': '1.00'}]

    response = client_for(admin).patch(detail_url(dinner.id), {'debts': debts}, format='json')

    assert response.status_code == 400
    assert response.json() == {'debts': [services.DEBT_NOT_FOUND]}
    other_debt.refresh_from_db()
    assert other_debt.amount == Decimal('100.00')
    assert dinner.debts.count() == 0


def test_edit_amount_below_open_debts_returns_400(admin, dinner):
    make_debt(dinner)

    response = client_for(admin).patch(detail_url(dinner.id), {'amount': '99.99'}, format='json')

    assert response.status_code == 400
    assert response.json() == {'debts': [services.DEBTS_EXCEED_AMOUNT]}
    dinner.refresh_from_db()
    assert dinner.amount == Decimal('300.00')


def test_edit_person_to_debtor_returns_400(admin, member, dinner):
    make_debt(dinner, debtor=member)

    response = client_for(admin).patch(
        detail_url(dinner.id), {'person': str(member.id)}, format='json'
    )

    assert response.status_code == 400
    assert response.json() == {'debts': [services.DEBTOR_IS_PAYER]}
    dinner.refresh_from_db()
    assert dinner.person == admin


# Datorii deschise

DEBTS_URL = reverse('debt-list')


def test_open_debts_response_format(admin, member, dinner):
    debt = make_debt(dinner, debtor=member)

    response = client_for(member).get(DEBTS_URL)

    assert response.status_code == 200
    assert response.json() == {
        'debts': [
            {
                'id': str(debt.id),
                'debtor': str(member.id),
                'debtor_name': '',
                'debtor_label': 'membru',
                'amount': '100.00',
                'status': 'open',
                'settled_at': None,
                'expense': str(dinner.id),
                'expense_date': '2026-11-05',
                'expense_store': 'La Plăcinte',
                'expense_amount': '300.00',
                'payer_name': 'admin',
            }
        ]
    }


def test_open_debts_lists_only_open_debts_from_all_months(admin, subcategory):
    october = make_expense(admin, subcategory, date=datetime.date(2026, 10, 3))
    november = make_expense(admin, subcategory, date=datetime.date(2026, 11, 20))
    make_debt(october, amount='1.00', debtor_name='Octombrie')
    make_debt(november, amount='2.00', debtor_name='Noiembrie')
    close_debt(make_debt(november, amount='3.00', debtor_name='Întoarsă'), CLOSED_STATUSES[0])
    close_debt(make_debt(october, amount='4.00', debtor_name='Anulată'), CLOSED_STATUSES[1])

    response = client_for(admin).get(DEBTS_URL)

    # Cele mai noi cheltuieli primele.
    assert [d['debtor_label'] for d in response.json()['debts']] == ['Noiembrie', 'Octombrie']


def test_open_debts_are_isolated_by_household(other_admin, dinner):
    make_debt(dinner)

    response = client_for(other_admin).get(DEBTS_URL)

    assert response.json() == {'debts': []}


def test_open_debts_query_count_does_not_grow(admin, member, dinner, django_assert_num_queries):
    make_debt(dinner, debtor=member)
    make_debt(dinner, debtor_name='Ion')
    make_debt(dinner, debtor_name='Ana')
    client = client_for(admin)

    # O singură interogare, cu JOIN-uri spre datornic, cheltuială și plătitor.
    with django_assert_num_queries(1):
        response = client.get(DEBTS_URL)

    assert len(response.json()['debts']) == 3


def test_open_debts_without_household_returns_403(user):
    response = client_for(user).get(DEBTS_URL)

    assert response.status_code == 403


# Întoarcerea datoriei


def settle_url(debt_id):
    return reverse('debt-settle', args=[debt_id])


def cancel_url(debt_id):
    return reverse('debt-cancel', args=[debt_id])


def settle(user, debt, amount):
    return client_for(user).post(settle_url(debt.id), {'amount': amount}, format='json')


def test_member_settling_whole_expense_becomes_its_payer(admin, member, dinner):
    debt = make_debt(dinner, amount='300.00', debtor=member)

    response = settle(admin, debt, '300.00')

    assert response.status_code == 204
    dinner.refresh_from_db()
    assert (dinner.person, dinner.amount) == (member, Decimal('300.00'))
    assert Expense.objects.count() == 1
    # Cheltuiala e acum a lui: datoria față de vechiul plătitor nu mai rămâne pe ea.
    assert ExpenseDebt.objects.count() == 0


def test_member_settling_rest_in_steps_ends_without_debts(admin, member, dinner):
    debt = make_debt(dinner, amount='300.00', debtor=member)

    settle(admin, debt, '100.00')
    rest = ExpenseDebt.objects.get(status=ExpenseDebt.Status.OPEN)
    response = settle(admin, rest, '200.00')

    assert response.status_code == 204
    dinner.refresh_from_db()
    assert (dinner.person, dinner.amount) == (member, Decimal('200.00'))
    copy = Expense.objects.exclude(pk=dinner.pk).get()
    assert (copy.person, copy.amount) == (member, Decimal('100.00'))
    assert ExpenseDebt.objects.count() == 0


def test_member_settling_part_gets_identical_expense(admin, member, dinner):
    debt = make_debt(dinner, amount='100.00', debtor=member)

    response = settle(admin, debt, '100.00')

    assert response.status_code == 204
    dinner.refresh_from_db()
    assert (dinner.person, dinner.amount) == (admin, Decimal('200.00'))
    copy = Expense.objects.exclude(pk=dinner.pk).get()
    assert (copy.person, copy.amount) == (member, Decimal('100.00'))
    assert (copy.household, copy.date, copy.category, copy.subcategory) == (
        dinner.household,
        dinner.date,
        dinner.category,
        dinner.subcategory,
    )
    assert (copy.store, copy.note, copy.link) == ('La Plăcinte', 'Cină', 'https://bon.md/1')
    assert copy.debts.count() == 0


def test_external_settling_part_reduces_expense(admin, dinner):
    debt = make_debt(dinner, amount='100.00')

    response = settle(admin, debt, '100.00')

    assert response.status_code == 204
    dinner.refresh_from_db()
    assert (dinner.person, dinner.amount) == (admin, Decimal('200.00'))
    assert Expense.objects.count() == 1


def test_external_settling_whole_expense_deletes_it(admin, dinner):
    debt = make_debt(dinner, amount='300.00')

    response = settle(admin, debt, '300.00')

    assert response.status_code == 204
    assert Expense.objects.count() == 0
    assert ExpenseDebt.objects.count() == 0


def test_partial_settle_leaves_rest_open(admin, dinner):
    debt = make_debt(dinner, amount='100.00')

    response = settle(admin, debt, '40.00')

    assert response.status_code == 204
    debt.refresh_from_db()
    assert (debt.status, debt.amount) == (ExpenseDebt.Status.SETTLED, Decimal('40.00'))
    rest = dinner.debts.get(status=ExpenseDebt.Status.OPEN)
    assert (rest.debtor_name, rest.amount) == ('Ion', Decimal('60.00'))
    dinner.refresh_from_db()
    assert dinner.amount == Decimal('260.00')


def test_partial_settle_of_member_keeps_member_on_rest(admin, member, dinner):
    debt = make_debt(dinner, amount='100.00', debtor=member)

    settle(admin, debt, '30.00')

    rest = dinner.debts.get(status=ExpenseDebt.Status.OPEN)
    assert (rest.debtor, rest.debtor_name, rest.amount) == (member, '', Decimal('70.00'))


def test_settling_debts_one_after_another(admin, member, dinner):
    ion = make_debt(dinner, amount='100.00')
    maria = make_debt(dinner, amount='200.00', debtor=member)

    settle(admin, ion, '100.00')
    response = settle(admin, maria, '200.00')

    # După ce Ion și-a întors partea, datoria membrului acoperă toată suma rămasă.
    assert response.status_code == 204
    dinner.refresh_from_db()
    assert (dinner.person, dinner.amount) == (member, Decimal('200.00'))
    assert Expense.objects.count() == 1


def test_debtor_can_confirm_own_settlement(member, dinner):
    debt = make_debt(dinner, debtor=member)

    response = settle(member, debt, '100.00')

    assert response.status_code == 204


def test_settle_more_than_debt_returns_400(admin, dinner):
    debt = make_debt(dinner)

    response = settle(admin, debt, '100.01')

    assert response.status_code == 400
    assert response.json() == {'amount': [services.SETTLE_EXCEEDS_DEBT]}
    debt.refresh_from_db()
    assert debt.status == ExpenseDebt.Status.OPEN
    dinner.refresh_from_db()
    assert dinner.amount == Decimal('300.00')


@pytest.mark.parametrize('amount', ['0', '-5', '', 'abc', None])
def test_settle_with_invalid_amount_returns_400(admin, dinner, amount):
    debt = make_debt(dinner)

    response = settle(admin, debt, amount)

    assert response.status_code == 400
    assert 'amount' in response.json()


@pytest.mark.parametrize('status', CLOSED_STATUSES)
def test_settle_closed_debt_returns_400(admin, dinner, status):
    debt = close_debt(make_debt(dinner), status)

    response = settle(admin, debt, '100.00')

    assert response.status_code == 400
    assert response.json() == {'non_field_errors': [services.DEBT_NOT_OPEN]}
    dinner.refresh_from_db()
    assert dinner.amount == Decimal('300.00')


def test_settle_debt_of_other_household_returns_404(other_admin, dinner):
    debt = make_debt(dinner)

    response = settle(other_admin, debt, '100.00')

    assert response.status_code == 404
    debt.refresh_from_db()
    assert debt.status == ExpenseDebt.Status.OPEN


def test_settle_unknown_debt_returns_404(admin):
    response = client_for(admin).post(
        settle_url('00000000-0000-0000-0000-000000000000'), {'amount': '1.00'}, format='json'
    )

    assert response.status_code == 404


def test_settle_without_household_returns_403(user, dinner):
    response = settle(user, make_debt(dinner), '100.00')

    assert response.status_code == 403


def test_settle_requires_csrf(admin, dinner):
    debt = make_debt(dinner)
    client = APIClient(enforce_csrf_checks=True)
    client.force_login(admin)

    response = client.post(settle_url(debt.id), {'amount': '100.00'}, format='json')

    assert response.status_code == 403
    debt.refresh_from_db()
    assert debt.status == ExpenseDebt.Status.OPEN


# Anularea datoriei


def test_cancel_debt_keeps_expense_unchanged(admin, dinner):
    debt = make_debt(dinner)

    response = client_for(admin).post(cancel_url(debt.id))

    assert response.status_code == 204
    debt.refresh_from_db()
    assert debt.status == ExpenseDebt.Status.CANCELED
    assert debt.settled_at == timezone.localdate()
    assert debt.amount == Decimal('100.00')
    dinner.refresh_from_db()
    assert (dinner.person, dinner.amount) == (admin, Decimal('300.00'))


@pytest.mark.parametrize('status', CLOSED_STATUSES)
def test_cancel_closed_debt_returns_400(admin, dinner, status):
    debt = close_debt(make_debt(dinner), status)

    response = client_for(admin).post(cancel_url(debt.id))

    assert response.status_code == 400
    assert response.json() == {'non_field_errors': [services.DEBT_NOT_OPEN]}


def test_cancel_debt_of_other_household_returns_404(other_admin, dinner):
    debt = make_debt(dinner)

    response = client_for(other_admin).post(cancel_url(debt.id))

    assert response.status_code == 404
    debt.refresh_from_db()
    assert debt.status == ExpenseDebt.Status.OPEN


def test_cancel_requires_csrf(admin, dinner):
    debt = make_debt(dinner)
    client = APIClient(enforce_csrf_checks=True)
    client.force_login(admin)

    response = client.post(cancel_url(debt.id))

    assert response.status_code == 403
    debt.refresh_from_db()
    assert debt.status == ExpenseDebt.Status.OPEN
