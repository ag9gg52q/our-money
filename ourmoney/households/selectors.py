from django.contrib.auth import get_user_model


def household_members(*, household_id):
    return get_user_model().objects.filter(household_id=household_id).order_by('role', 'username')
