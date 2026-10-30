from .models import Category


def create_category(*, household_id, name):
    category = Category.objects.create(household_id=household_id, name=name)
    return category


def update_category(*, category, data):
    for field, value in data.items():
        setattr(category, field, value)
    category.save(update_fields=list(data))
    return category
