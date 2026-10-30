from .models import Subcategory


def household_subcategories(*, household_id):
    return Subcategory.objects.filter(category__household_id=household_id)
