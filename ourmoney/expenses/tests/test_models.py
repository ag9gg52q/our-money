import datetime
from decimal import Decimal

import pytest
from django.db import IntegrityError
from django.db.models import ProtectedError, RestrictedError

from categories.models import Category
from expenses.models import Expense, ExpenseDebt
from households.services import create_household, join_household
from subcategories.models import Subcategory
from users.models import User

pytestmark = pytest.mark.django_db


@pytest.fixture
def person():
    user = User.objects.create_user(username='ion', password='x')
    create_household(user=user, name='Familia Popescu')
    return user


@pytest.fixture
def category(person):
    return Category.objects.create(household=person.household, name='Alimente')


@pytest.fixture
def subcategory(category):
    return Subcategory.objects.create(category=category, name='Lactate')


def make_expense(person, category, **fields):
    data = {
        'household': person.household,
        'date': datetime.date(2026, 11, 5),
        'person': person,
        'category': category,
        'subcategory': category.subcategories.first(),
        'amount': Decimal('12.50'),
        'store': 'Kaufland',
    }
    data.update(fields)
    return Expense.objects.create(**data)


def test_expense_is_saved_with_empty_note(person, category, subcategory):
    expense = make_expense(person, category)

    expense.refresh_from_db()
    assert expense.subcategory == subcategory
    assert expense.store == 'Kaufland'
    assert expense.note == ''
    assert expense.amount == Decimal('12.50')
    assert str(expense) == '2026-11-05 - 12.50'


def test_expense_without_subcategory_is_rejected_by_database(person, category):
    with pytest.raises(IntegrityError):
        make_expense(person, category, subcategory=None)


def test_expenses_are_ordered_newest_first(person, category, subcategory):
    make_expense(person, category, date=datetime.date(2026, 11, 1), note='veche')
    make_expense(person, category, date=datetime.date(2026, 11, 3), note='nouă')

    assert [e.note for e in Expense.objects.all()] == ['nouă', 'veche']


def test_same_day_expenses_are_ordered_by_creation_newest_first(person, category, subcategory):
    make_expense(person, category, note='prima')
    make_expense(person, category, note='a doua')

    assert [e.note for e in Expense.objects.all()] == ['a doua', 'prima']


@pytest.mark.parametrize('amount', [Decimal('0'), Decimal('-5.00')])
def test_non_positive_amount_is_rejected_by_database(person, category, subcategory, amount):
    with pytest.raises(IntegrityError):
        make_expense(person, category, amount=amount)


def test_category_with_expenses_cannot_be_deleted(person, category, subcategory):
    make_expense(person, category)

    with pytest.raises(RestrictedError):
        category.delete()


def test_subcategory_with_expenses_cannot_be_deleted(person, category, subcategory):
    make_expense(person, category)

    with pytest.raises(RestrictedError):
        subcategory.delete()


def test_deleting_household_deletes_its_expenses(person, category, subcategory):
    make_expense(person, category)

    person.household.delete()

    assert Expense.objects.count() == 0


# Datorii


@pytest.fixture
def member(person):
    user = User.objects.create_user(username='maria', password='x')
    join_household(user=user, household=person.household)
    return user


@pytest.fixture
def expense(person, category, subcategory):
    return make_expense(person, category, amount=Decimal('300.00'))


def make_debt(expense, **fields):
    data = {'expense': expense, 'amount': Decimal('100.00')}
    data.update(fields)
    return ExpenseDebt.objects.create(**data)


def test_member_debt_is_saved_open(expense, member):
    debt = make_debt(expense, debtor=member)

    debt.refresh_from_db()
    assert debt.debtor == member
    assert debt.debtor_name == ''
    assert debt.status == ExpenseDebt.Status.OPEN
    assert debt.settled_at is None
    assert list(expense.debts.all()) == [debt]


def test_external_debt_is_saved(expense):
    debt = make_debt(expense, debtor_name='Ion')

    debt.refresh_from_db()
    assert debt.debtor is None
    assert str(debt) == 'Ion - 100.00'


@pytest.mark.parametrize('amount', [Decimal('0'), Decimal('-5.00')])
def test_debt_non_positive_amount_is_rejected_by_database(expense, member, amount):
    with pytest.raises(IntegrityError):
        make_debt(expense, debtor=member, amount=amount)


def test_debt_with_member_and_name_is_rejected_by_database(expense, member):
    with pytest.raises(IntegrityError):
        make_debt(expense, debtor=member, debtor_name='Ion')


def test_debt_without_member_or_name_is_rejected_by_database(expense):
    with pytest.raises(IntegrityError):
        make_debt(expense)


def test_second_open_debt_of_same_member_is_rejected_by_database(expense, member):
    make_debt(expense, debtor=member)

    with pytest.raises(IntegrityError):
        make_debt(expense, debtor=member)


def test_second_open_debt_of_same_name_ignores_case(expense):
    make_debt(expense, debtor_name='Ion')

    with pytest.raises(IntegrityError):
        make_debt(expense, debtor_name='ion')


@pytest.mark.parametrize('status', [ExpenseDebt.Status.SETTLED, ExpenseDebt.Status.CANCELED])
def test_closed_debt_allows_new_open_debt_of_same_person(expense, member, status):
    # Istoricul: după o întoarcere parțială, rândul întors rămâne lângă cel deschis.
    make_debt(expense, debtor=member, status=status, settled_at=datetime.date(2026, 11, 20))
    make_debt(expense, debtor_name='Ion', status=status, settled_at=datetime.date(2026, 11, 20))

    make_debt(expense, debtor=member)
    make_debt(expense, debtor_name='Ion')

    assert expense.debts.filter(status=ExpenseDebt.Status.OPEN).count() == 2


def test_same_person_can_owe_on_different_expenses(person, category, expense, member):
    other = make_expense(person, category)
    make_debt(expense, debtor=member)

    make_debt(other, debtor=member)

    assert ExpenseDebt.objects.filter(debtor=member).count() == 2


def test_debts_are_ordered_by_creation(expense):
    make_debt(expense, debtor_name='Ion')
    make_debt(expense, debtor_name='Ana')

    assert [d.debtor_name for d in expense.debts.all()] == ['Ion', 'Ana']


def test_deleting_expense_deletes_its_debts(expense, member):
    make_debt(expense, debtor=member)
    make_debt(expense, debtor_name='Ion')

    expense.delete()

    assert ExpenseDebt.objects.count() == 0


def test_member_with_debts_cannot_be_deleted(expense, member):
    make_debt(expense, debtor=member)

    with pytest.raises(ProtectedError):
        member.delete()
