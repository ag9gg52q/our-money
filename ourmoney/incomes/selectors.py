from decimal import Decimal

from django.db.models import Sum

from .models import Income


def household_incomes(*, household_id, date_from=None, date_to=None, person=None):
    incomes = Income.objects.filter(household_id=household_id)
    if date_from:
        incomes = incomes.filter(date__gte=date_from)
    if date_to:
        incomes = incomes.filter(date__lte=date_to)
    if person:
        incomes = incomes.filter(person=person)

    return incomes.select_related('person', 'income_source')


def incomes_total(*, incomes):
    return incomes.aggregate(total=Sum('amount'))['total'] or Decimal('0')
