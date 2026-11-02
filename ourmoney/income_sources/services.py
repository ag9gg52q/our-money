from .models import IncomeSource


def create_income_source(*, household_id, name):
    income_source = IncomeSource.objects.create(name=name, household_id=household_id)
    return income_source


def update_income_source(*, income_source, data):
    for field, value in data.items():
        setattr(income_source, field, value)
    income_source.save(update_fields=list(data))
    return income_source
