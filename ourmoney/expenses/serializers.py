from decimal import Decimal

from rest_framework import serializers

from categories.selectors import household_categories
from households.selectors import household_members
from subcategories.selectors import household_subcategories

from .models import Expense


def with_current(queryset, current_id):
    if current_id is None:
        return queryset
    return queryset | queryset.model.objects.filter(pk=current_id)


class ExpenseSerializer(serializers.ModelSerializer):
    person_name = serializers.CharField(source='person.username', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    subcategory_name = serializers.CharField(source='subcategory.name', read_only=True)

    class Meta:
        model = Expense
        fields = (
            'id',
            'date',
            'amount',
            'note',
            'person',
            'person_name',
            'category',
            'category_name',
            'subcategory',
            'subcategory_name',
        )
        read_only_fields = ('id',)
        extra_kwargs = {'amount': {'min_value': Decimal('0.01')}}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        household_id = self.context['request'].user.household_id
        current = self.instance if isinstance(self.instance, Expense) else None

        self.fields['person'].queryset = with_current(
            household_members(household_id=household_id),
            getattr(current, 'person_id', None),
        )
        self.fields['category'].queryset = with_current(
            household_categories(household_id=household_id).filter(is_active=True),
            getattr(current, 'category_id', None),
        )
        self.fields['subcategory'].queryset = with_current(
            household_subcategories(household_id=household_id).filter(is_active=True),
            getattr(current, 'subcategory_id', None),
        )

    def validate(self, attrs):
        # La editare parțială (PATCH) câmpurile netrimise își păstrează valoarea curentă.
        category = attrs.get('category', getattr(self.instance, 'category', None))
        subcategory = attrs.get('subcategory', getattr(self.instance, 'subcategory', None))
        if subcategory.category_id != category.id:
            raise serializers.ValidationError(
                {'subcategory': 'Subcategoria nu aparține categoriei alese.'}
            )
        return attrs


class ExpenseFilterSerializer(serializers.Serializer):
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)
    category = serializers.UUIDField(required=False)
    subcategory = serializers.UUIDField(required=False)
    person = serializers.UUIDField(required=False)

    def validate(self, attrs):
        date_from = attrs.get('date_from')
        date_to = attrs.get('date_to')
        if date_from and date_to and date_from > date_to:
            raise serializers.ValidationError(
                {'date_to': 'Data de sfârșit nu poate fi înainte de data de început.'}
            )
        return attrs
