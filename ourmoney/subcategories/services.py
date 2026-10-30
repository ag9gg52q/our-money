from .models import Subcategory


def create_subcategory(*, category_id, name):
    subcategory = Subcategory.objects.create(category_id=category_id, name=name)
    return subcategory


def update_subcategory(*, subcategory, data):
    for field, value in data.items():
        setattr(subcategory, field, value)
    subcategory.save(update_fields=list(data))
    return subcategory
