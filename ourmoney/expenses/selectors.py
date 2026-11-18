from decimal import Decimal

from django.db.models import Sum

from .models import Expense


def household_expenses(
    *, household_id, date_from=None, date_to=None, category=None, subcategory=None, person=None
):
    expenses = Expense.objects.filter(household_id=household_id)
    if date_from:
        expenses = expenses.filter(date__gte=date_from)
    if date_to:
        expenses = expenses.filter(date__lte=date_to)
    if category:
        expenses = expenses.filter(category=category)
    if subcategory:
        expenses = expenses.filter(subcategory=subcategory)
    if person:
        expenses = expenses.filter(person=person)

    return expenses.select_related('person', 'category', 'subcategory')


def expenses_total(*, expenses):
    return expenses.aggregate(total=Sum('amount'))['total'] or Decimal('0')
