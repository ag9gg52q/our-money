import uuid

from django.conf import settings
from django.db import models


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
    note = models.CharField(max_length=255, blank=True)
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
