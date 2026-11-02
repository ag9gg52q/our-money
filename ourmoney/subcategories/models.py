import uuid

from django.db import models
from django.db.models.functions import Lower


class Subcategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(
        'categories.Category', on_delete=models.CASCADE, related_name='subcategories'
    )
    name = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(
                'category',
                Lower('name'),
                name='unique_subcategory_name_per_category',
                violation_error_message=(
                    'Există deja o subcategorie cu acest nume în această categorie.'
                ),
            ),
        ]

    def __str__(self):
        return self.name
