from decimal import Decimal

from django.db import transaction
from django.db.models import Sum
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from .models import Expense, ExpenseDebt

DEBTS_EXCEED_AMOUNT = 'Datoriile depășesc suma cheltuielii.'
DEBTOR_IS_PAYER = 'Persoana care a plătit nu își poate datora sieși.'
DEBT_NOT_FOUND = 'Datoria nu există sau nu mai este deschisă.'
DEBT_NOT_OPEN = 'Datoria nu mai este deschisă.'
SETTLE_EXCEEDS_DEBT = 'Suma întoarsă nu poate depăși datoria.'

OPEN = ExpenseDebt.Status.OPEN


@transaction.atomic
def create_expense(*, household_id, data):
    data = dict(data)
    debts = data.pop('debts', [])

    expense = Expense.objects.create(household_id=household_id, **data)
    _save_open_debts(expense=expense, debts=debts)
    _check_open_debts(expense=expense)
    return expense


@transaction.atomic
def update_expense(*, expense, data):
    data = dict(data)
    debts = data.pop('debts', None)
    for field, value in data.items():
        setattr(expense, field, value)
    expense.save(update_fields=[*data, 'updated_at'])

    if debts is not None:
        _save_open_debts(expense=expense, debts=debts)
        expense.refresh_from_db(fields=['debts'])
    _check_open_debts(expense=expense)
    return expense


def delete_expense(*, expense):
    expense.delete()


def _save_open_debts(*, expense, debts):
    open_debts = {debt.id: debt for debt in expense.debts.filter(status=OPEN)}
    kept_ids = {item['id'] for item in debts if item.get('id')}
    if kept_ids - open_debts.keys():
        raise ValidationError({'debts': [DEBT_NOT_FOUND]})

    expense.debts.filter(status=OPEN).exclude(id__in=kept_ids).delete()

    for item in debts:
        fields = {
            'debtor': item.get('debtor'),
            'debtor_name': item.get('debtor_name', ''),
            'amount': item['amount'],
        }
        if item.get('id'):
            debt = open_debts[item['id']]
            for field, value in fields.items():
                setattr(debt, field, value)
            debt.save(update_fields=[*fields, 'updated_at'])
        else:
            ExpenseDebt.objects.create(expense=expense, **fields)


def _check_open_debts(*, expense):
    open_debts = expense.debts.filter(status=OPEN)
    total = open_debts.aggregate(total=Sum('amount'))['total'] or Decimal('0')
    if total > expense.amount:
        raise ValidationError({'debts': [DEBTS_EXCEED_AMOUNT]})
    if open_debts.filter(debtor_id=expense.person_id).exists():
        raise ValidationError({'debts': [DEBTOR_IS_PAYER]})


@transaction.atomic
def settle_debt(*, debt, amount):
    expense = Expense.objects.select_for_update().get(pk=debt.expense_id)
    debt = ExpenseDebt.objects.select_for_update().get(pk=debt.pk)

    if debt.status != OPEN:
        raise ValidationError({'non_field_errors': [DEBT_NOT_OPEN]})
    if amount > debt.amount:
        raise ValidationError({'amount': [SETTLE_EXCEEDS_DEBT]})

    remaining = debt.amount - amount
    debt.amount = amount
    debt.status = ExpenseDebt.Status.SETTLED
    debt.settled_at = timezone.localdate()
    debt.save(update_fields=['amount', 'status', 'settled_at', 'updated_at'])

    if remaining:
        ExpenseDebt.objects.create(
            expense=expense,
            debtor_id=debt.debtor_id,
            debtor_name=debt.debtor_name,
            amount=remaining,
        )

    if debt.debtor_id and amount == expense.amount:
        expense.person_id = debt.debtor_id
        expense.save(update_fields=['person', 'updated_at'])
    elif debt.debtor_id:
        _copy_expense(expense=expense, person_id=debt.debtor_id, amount=amount)
        _reduce_expense(expense=expense, amount=amount)
    elif amount == expense.amount:
        expense.delete()
    else:
        _reduce_expense(expense=expense, amount=amount)


@transaction.atomic
def cancel_debt(*, debt):
    debt = ExpenseDebt.objects.select_for_update().get(pk=debt.pk)
    if debt.status != OPEN:
        raise ValidationError({'non_field_errors': [DEBT_NOT_OPEN]})

    debt.status = ExpenseDebt.Status.CANCELED
    debt.settled_at = timezone.localdate()
    debt.save(update_fields=['status', 'settled_at', 'updated_at'])


def _copy_expense(*, expense, person_id, amount):
    return Expense.objects.create(
        household_id=expense.household_id,
        date=expense.date,
        person_id=person_id,
        category_id=expense.category_id,
        subcategory_id=expense.subcategory_id,
        amount=amount,
        store=expense.store,
        note=expense.note,
        link=expense.link,
    )


def _reduce_expense(*, expense, amount):
    expense.amount -= amount
    expense.save(update_fields=['amount', 'updated_at'])
