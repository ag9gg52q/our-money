import uuid

from django.db import models
from django.db.models.functions import Lower


class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    household = models.ForeignKey(
        'households.Household', on_delete=models.CASCADE, related_name='categories'
    )
    name = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(
                'household',
                Lower('name'),
                name='unique_category_name_per_household',
                violation_error_message='Există deja o categorie cu acest nume în gospodărie.',
            ),
        ]

    def __str__(self):
        return self.name
