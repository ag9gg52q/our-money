from collections.abc import Mapping
from decimal import Decimal

from rest_framework import serializers

from households.selectors import household_members
from income_sources.selectors import household_income_sources

from .models import Income

REQUIRED_FIELDS = ('date', 'amount', 'person', 'income_source')
EMPTY_MESSAGE = 'Acest câmp nu poate fi gol.'
EMPTY_ERRORS = {'required': EMPTY_MESSAGE, 'null': EMPTY_MESSAGE, 'blank': EMPTY_MESSAGE}


def with_current(queryset, current_id):
    if current_id is None:
        return queryset
    return queryset | queryset.model.objects.filter(pk=current_id)


class IncomeSerializer(serializers.ModelSerializer):
    person_name = serializers.CharField(source='person.username', read_only=True)
    income_source_name = serializers.CharField(source='income_source.name', read_only=True)

    class Meta:
        model = Income
        fields = (
            'id',
            'date',
            'amount',
            'note',
            'person',
            'person_name',
            'income_source',
            'income_source_name',
        )
        read_only_fields = ('id',)
        extra_kwargs = {
            **{field: {'error_messages': EMPTY_ERRORS} for field in REQUIRED_FIELDS},
            'amount': {'min_value': Decimal('0.01'), 'error_messages': EMPTY_ERRORS},
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        household_id = self.context['request'].user.household_id
        current = self.instance if isinstance(self.instance, Income) else None

        self.fields['person'].queryset = with_current(
            household_members(household_id=household_id),
            getattr(current, 'person_id', None),
        )
        self.fields['income_source'].queryset = with_current(
            household_income_sources(household_id=household_id).filter(is_active=True),
            getattr(current, 'income_source_id', None),
        )

    def to_internal_value(self, data):
        if isinstance(data, Mapping):
            data = {**data, **{f: None for f in REQUIRED_FIELDS if data.get(f) == ''}}
        return super().to_internal_value(data)


class IncomeFilterSerializer(serializers.Serializer):
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)
    person = serializers.UUIDField(required=False)

    def validate(self, attrs):
        date_from = attrs.get('date_from')
        date_to = attrs.get('date_to')
        if date_from and date_to and date_from > date_to:
            raise serializers.ValidationError(
                {'date_to': 'Data de sfârșit nu poate fi înainte de data de început.'}
            )
        return attrs
