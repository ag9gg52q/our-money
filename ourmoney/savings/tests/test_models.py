import datetime
from decimal import Decimal

import pytest
from django.db import IntegrityError
from django.db.models import ProtectedError

from households.services import create_household
from savings.models import SavingsEntry
from users.models import User

pytestmark = pytest.mark.django_db


@pytest.fixture
def person():
    user = User.objects.create_user(username='ion', password='x')
    create_household(user=user, name='Familia Popescu')
    return user


def make_entry(person, **fields):
    data = {
        'household': person.household,
        'date': datetime.date(2026, 11, 5),
        'person': person,
        'amount': Decimal('1000.00'),
    }
    data.update(fields)
    return SavingsEntry.objects.create(**data)


def test_deposit_is_saved_with_empty_note(person):
    entry = make_entry(person)

    entry.refresh_from_db()
    assert entry.amount == Decimal('1000.00')
    assert entry.note == ''
    assert str(entry) == '2026-11-05 - 1000.00'


def test_withdrawal_is_saved_as_negative_amount(person):
    entry = make_entry(person, amount=Decimal('-500.00'))

    entry.refresh_from_db()
    assert entry.amount == Decimal('-500.00')


def test_zero_amount_is_rejected_by_database(person):
    with pytest.raises(IntegrityError):
        make_entry(person, amount=Decimal('0'))


def test_entries_are_ordered_newest_first(person):
    make_entry(person, date=datetime.date(2026, 11, 1), note='vechi')
    make_entry(person, date=datetime.date(2026, 11, 3), note='nou')

    assert [e.note for e in SavingsEntry.objects.all()] == ['nou', 'vechi']


def test_same_day_entries_are_ordered_by_creation_newest_first(person):
    make_entry(person, note='primul')
    make_entry(person, note='al doilea')

    assert [e.note for e in SavingsEntry.objects.all()] == ['al doilea', 'primul']


def test_person_with_entries_cannot_be_deleted(person):
    make_entry(person)

    with pytest.raises(ProtectedError):
        person.delete()


def test_deleting_household_deletes_its_entries(person):
    make_entry(person)

    person.household.delete()

    assert SavingsEntry.objects.count() == 0
