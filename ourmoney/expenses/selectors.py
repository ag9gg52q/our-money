from decimal import Decimal

from django.db.models import Prefetch, Sum

from .models import Expense, ExpenseDebt


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

    debts = Prefetch('debts', queryset=ExpenseDebt.objects.select_related('debtor'))
    return expenses.select_related('person', 'category', 'subcategory').prefetch_related(debts)


def household_open_debts(*, household_id):
    return (
        household_debts(household_id=household_id)
        .filter(status=ExpenseDebt.Status.OPEN)
        .select_related('debtor', 'expense__person')
        .order_by('-expense__date', 'created_at')
    )


def household_debts(*, household_id):
    return ExpenseDebt.objects.filter(expense__household_id=household_id)


def expenses_total(*, expenses):
    return expenses.aggregate(total=Sum('amount'))['total'] or Decimal('0')
