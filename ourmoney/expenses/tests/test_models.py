import datetime
from decimal import Decimal

import pytest
from django.db import IntegrityError
from django.db.models import RestrictedError

from categories.models import Category
from expenses.models import Expense
from households.services import create_household
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
