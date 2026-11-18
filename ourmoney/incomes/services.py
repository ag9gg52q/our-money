from .models import Income


def create_income(*, household_id, data):
    income = Income.objects.create(household_id=household_id, **data)
    return income


def update_income(*, income, data):
    for field, value in data.items():
        setattr(income, field, value)
    income.save(update_fields=[*data, 'updated_at'])
    return income


def delete_income(*, income):
    income.delete()
