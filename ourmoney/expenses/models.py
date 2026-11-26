import uuid

from django.conf import settings
from django.db import models
from django.db.models.functions import Lower

DUPLICATE_OPEN_DEBT = 'Persoana are deja o datorie deschisă pe această cheltuială.'


class Expense(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    household = models.ForeignKey(
        'households.Household', on_delete=models.CASCADE, related_name='expenses'
    )
    date = models.DateField()
    person = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='expenses'
    )
    category = models.ForeignKey(
        'categories.Category', on_delete=models.RESTRICT, related_name='expenses'
    )
    subcategory = models.ForeignKey(
        'subcategories.Subcategory', on_delete=models.RESTRICT, related_name='expenses'
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    store = models.CharField(max_length=100)
    note = models.CharField(max_length=255, blank=True)
    link = models.URLField(max_length=1000, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']
        constraints = [
            models.CheckConstraint(
                condition=models.Q(amount__gt=0),
                name='expense_amount_positive',
                violation_error_message='Suma trebuie să fie mai mare decât zero.',
            ),
        ]

        indexes = [models.Index(fields=['household', 'date'])]

    def __str__(self):
        return f'{self.date} - {self.amount}'


class ExpenseDebt(models.Model):
    class Status(models.TextChoices):
        OPEN = 'open', 'Deschisă'
        SETTLED = 'settled', 'Întoarsă'
        CANCELED = 'canceled', 'Anulată'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE, related_name='debts')
    # Datornicul e fie un membru al gospodăriei (debtor), fie o persoană din afară (debtor_name).
    debtor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='expense_debts',
        null=True,
        blank=True,
    )
    debtor_name = models.CharField(max_length=100, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.OPEN)
    settled_at = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']
        constraints = [
            models.CheckConstraint(
                condition=models.Q(amount__gt=0),
                name='expense_debt_amount_positive',
                violation_error_message='Suma trebuie să fie mai mare decât zero.',
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(debtor__isnull=False, debtor_name='')
                    | (models.Q(debtor__isnull=True) & ~models.Q(debtor_name=''))
                ),
                name='expense_debt_member_or_name',
                violation_error_message='Alege un membru sau scrie un nume.',
            ),
            models.UniqueConstraint(
                fields=['expense', 'debtor'],
                condition=models.Q(debtor__isnull=False, status='open'),
                name='unique_open_debt_per_member',
                violation_error_message=DUPLICATE_OPEN_DEBT,
            ),
            models.UniqueConstraint(
                'expense',
                Lower('debtor_name'),
                condition=~models.Q(debtor_name='') & models.Q(status='open'),
                name='unique_open_debt_per_name',
                violation_error_message=DUPLICATE_OPEN_DEBT,
            ),
        ]

    def __str__(self):
        return f'{self.debtor_name or self.debtor} - {self.amount}'
