from .models import Expense


def create_expense(*, household_id, data):
    expense = Expense.objects.create(household_id=household_id, **data)
    return expense


def update_expense(*, expense, data):
    for field, value in data.items():
        setattr(expense, field, value)
    expense.save(update_fields=[*data, 'updated_at'])
    return expense


def delete_expense(*, expense):
    expense.delete()
