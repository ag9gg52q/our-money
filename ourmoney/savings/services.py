from rest_framework.exceptions import ValidationError

from .models import SavingsEntry
from .selectors import savings_summary

NEGATIVE_BALANCE_MESSAGE = 'Soldul economiilor nu poate deveni negativ.'


def _balance(household_id):
    return savings_summary(household_id=household_id)['balance']


def create_savings_entry(*, household_id, data):
    if _balance(household_id) + data['amount'] < 0:
        raise ValidationError({'amount': [NEGATIVE_BALANCE_MESSAGE]})

    return SavingsEntry.objects.create(household_id=household_id, **data)


def update_savings_entry(*, savings_entry, data):
    new_amount = data.get('amount', savings_entry.amount)
    if _balance(savings_entry.household_id) - savings_entry.amount + new_amount < 0:
        raise ValidationError({'amount': [NEGATIVE_BALANCE_MESSAGE]})

    for field, value in data.items():
        setattr(savings_entry, field, value)
    savings_entry.save(update_fields=[*data, 'updated_at'])
    return savings_entry


def delete_savings_entry(*, savings_entry):
    if _balance(savings_entry.household_id) - savings_entry.amount < 0:
        raise ValidationError({'non_field_errors': [NEGATIVE_BALANCE_MESSAGE]})

    savings_entry.delete()
