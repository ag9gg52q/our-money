import datetime
from decimal import Decimal

import pytest
from django.db import IntegrityError
from django.db.models import RestrictedError

from households.services import create_household
from income_sources.models import IncomeSource
from incomes.models import Income
from users.models import User

pytestmark = pytest.mark.django_db


@pytest.fixture
def person():
    user = User.objects.create_user(username='ion', password='x')
    create_household(user=user, name='Familia Popescu')
    return user


@pytest.fixture
def income_source(person):
    return IncomeSource.objects.create(household=person.household, name='Salariu')


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


def test_income_is_saved_with_empty_note(person, income_source):
    income = make_income(person, income_source)

    income.refresh_from_db()
    assert income.income_source == income_source
    assert income.note == ''
    assert income.amount == Decimal('5000.00')
    assert str(income) == '2026-11-05 - 5000.00'


def test_income_without_source_is_rejected_by_database(person):
    with pytest.raises(IntegrityError):
        make_income(person, None)


def test_incomes_are_ordered_newest_first(person, income_source):
    make_income(person, income_source, date=datetime.date(2026, 11, 1), note='vechi')
    make_income(person, income_source, date=datetime.date(2026, 11, 3), note='nou')

    assert [i.note for i in Income.objects.all()] == ['nou', 'vechi']


def test_same_day_incomes_are_ordered_by_creation_newest_first(person, income_source):
    make_income(person, income_source, note='primul')
    make_income(person, income_source, note='al doilea')

    assert [i.note for i in Income.objects.all()] == ['al doilea', 'primul']


@pytest.mark.parametrize('amount', [Decimal('0'), Decimal('-5.00')])
def test_non_positive_amount_is_rejected_by_database(person, income_source, amount):
    with pytest.raises(IntegrityError):
        make_income(person, income_source, amount=amount)


def test_income_source_with_incomes_cannot_be_deleted(person, income_source):
    make_income(person, income_source)

    with pytest.raises(RestrictedError):
        income_source.delete()


def test_deleting_household_deletes_its_incomes(person, income_source):
    make_income(person, income_source)

    person.household.delete()

    assert Income.objects.count() == 0
