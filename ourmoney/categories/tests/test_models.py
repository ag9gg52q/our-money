import pytest
from django.db import IntegrityError

from categories.models import Category
from households.models import Household

pytestmark = pytest.mark.django_db


@pytest.fixture
def household():
    return Household.objects.create(name='Familia Popescu')


def test_new_category_is_active(household):
    category = Category.objects.create(household=household, name='Alimente')

    assert category.is_active is True
    assert str(category) == 'Alimente'


def test_categories_are_ordered_by_name(household):
    Category.objects.create(household=household, name='Transport')
    Category.objects.create(household=household, name='Alimente')

    assert [c.name for c in Category.objects.all()] == ['Alimente', 'Transport']


def test_duplicate_name_in_household_is_rejected_by_database(household):
    Category.objects.create(household=household, name='Alimente')

    with pytest.raises(IntegrityError):
        Category.objects.create(household=household, name='ALIMENTE')


def test_same_name_allowed_in_different_households(household):
    other = Household.objects.create(name='Familia Ionescu')
    Category.objects.create(household=household, name='Alimente')
    Category.objects.create(household=other, name='Alimente')

    assert Category.objects.count() == 2


def test_deleting_household_deletes_its_categories(household):
    Category.objects.create(household=household, name='Alimente')

    household.delete()

    assert Category.objects.count() == 0
