from .models import IncomeSource


def household_income_sources(*, household_id):
    return IncomeSource.objects.filter(household_id=household_id)
