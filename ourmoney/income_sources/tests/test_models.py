import pytest
from django.db import IntegrityError

from households.models import Household
from income_sources.models import IncomeSource

pytestmark = pytest.mark.django_db


@pytest.fixture
def household():
    return Household.objects.create(name='Familia Popescu')


def test_new_income_source_is_active(household):
    income_source = IncomeSource.objects.create(household=household, name='Bonus')

    assert income_source.is_active is True
    assert str(income_source) == 'Bonus'


def test_income_sources_are_ordered_by_name(household):
    IncomeSource.objects.create(household=household, name='Salariu')
    IncomeSource.objects.create(household=household, name='Bonus')

    assert [c.name for c in IncomeSource.objects.all()] == ['Bonus', 'Salariu']


def test_duplicate_name_in_household_is_rejected_by_database(household):
    IncomeSource.objects.create(household=household, name='Bonus')

    with pytest.raises(IntegrityError):
        IncomeSource.objects.create(household=household, name='BONUS')


def test_same_name_allowed_in_different_households(household):
    other = Household.objects.create(name='Familia Ionescu')
    IncomeSource.objects.create(household=household, name='Bonus')
    IncomeSource.objects.create(household=other, name='Bonus')

    assert IncomeSource.objects.count() == 2


def test_deleting_household_deletes_its_income_sources(household):
    IncomeSource.objects.create(household=household, name='Bonus')

    household.delete()

    assert IncomeSource.objects.count() == 0
