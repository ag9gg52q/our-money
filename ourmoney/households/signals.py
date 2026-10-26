from django.db.models.signals import pre_delete
from django.dispatch import receiver

from .models import Household


@receiver(pre_delete, sender=Household)
def remove_members_role(sender, instance, **kwargs):
    instance.members.update(role='')
