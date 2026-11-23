from decimal import Decimal

from django.db.models import Q, Sum
from django.db.models.functions import Coalesce

from .models import SavingsEntry


def household_savings_entries(*, household_id):
    return SavingsEntry.objects.filter(household_id=household_id).select_related('person')


def savings_summary(*, household_id):
    zero = Decimal('0')
    return SavingsEntry.objects.filter(household_id=household_id).aggregate(
        balance=Coalesce(Sum('amount'), zero),
        deposits=Coalesce(Sum('amount', filter=Q(amount__gt=0)), zero),
        withdrawals=Coalesce(Sum('amount', filter=Q(amount__lt=0)), zero),
    )
