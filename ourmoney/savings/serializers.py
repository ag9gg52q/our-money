from collections.abc import Mapping

from rest_framework import serializers

from households.selectors import household_members

from .models import SavingsEntry

REQUIRED_FIELDS = ('date', 'amount', 'person')
EMPTY_MESSAGE = 'Acest câmp nu poate fi gol.'
EMPTY_ERRORS = {'required': EMPTY_MESSAGE, 'null': EMPTY_MESSAGE, 'blank': EMPTY_MESSAGE}
ZERO_AMOUNT_MESSAGE = 'Suma trebuie să fie diferită de zero.'


def with_current(queryset, current_id):
    if current_id is None:
        return queryset
    return queryset | queryset.model.objects.filter(pk=current_id)


class SavingsEntrySerializer(serializers.ModelSerializer):
    person_name = serializers.CharField(source='person.username', read_only=True)

    class Meta:
        model = SavingsEntry
        fields = ('id', 'date', 'amount', 'note', 'person', 'person_name')
        read_only_fields = ('id',)
        extra_kwargs = {field: {'error_messages': EMPTY_ERRORS} for field in REQUIRED_FIELDS}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        household_id = self.context['request'].user.household_id
        current = self.instance if isinstance(self.instance, SavingsEntry) else None

        self.fields['person'].queryset = with_current(
            household_members(household_id=household_id),
            getattr(current, 'person_id', None),
        )

    def to_internal_value(self, data):
        if isinstance(data, Mapping):
            data = {**data, **{f: None for f in REQUIRED_FIELDS if data.get(f) == ''}}
        return super().to_internal_value(data)

    def validate_amount(self, value):
        if value == 0:
            raise serializers.ValidationError(ZERO_AMOUNT_MESSAGE)
        return value
