from .models import Category


def household_categories(*, household_id):
    return Category.objects.filter(household_id=household_id)
