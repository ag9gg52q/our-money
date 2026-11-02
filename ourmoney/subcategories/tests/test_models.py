import pytest
from django.db import IntegrityError

from categories.models import Category
from households.models import Household
from subcategories.models import Subcategory

pytestmark = pytest.mark.django_db


@pytest.fixture
def category():
    household = Household.objects.create(name='Familia Popescu')
    return Category.objects.create(household=household, name='Alimente')


def test_new_subcategory_is_active(category):
    subcategory = Subcategory.objects.create(category=category, name='Lactate')

    assert subcategory.is_active is True
    assert str(subcategory) == 'Lactate'


def test_subcategories_are_ordered_by_name(category):
    Subcategory.objects.create(category=category, name='Pâine')
    Subcategory.objects.create(category=category, name='Lactate')

    assert [s.name for s in Subcategory.objects.all()] == ['Lactate', 'Pâine']


def test_duplicate_name_in_category_is_rejected_by_database(category):
    Subcategory.objects.create(category=category, name='Lactate')

    with pytest.raises(IntegrityError):
        Subcategory.objects.create(category=category, name='LACTATE')


def test_same_name_allowed_in_different_categories(category):
    other = Category.objects.create(household=category.household, name='Transport')
    Subcategory.objects.create(category=category, name='Altele')
    Subcategory.objects.create(category=other, name='Altele')

    assert Subcategory.objects.count() == 2


def test_deleting_category_deletes_its_subcategories(category):
    Subcategory.objects.create(category=category, name='Lactate')

    category.delete()

    assert Subcategory.objects.count() == 0
