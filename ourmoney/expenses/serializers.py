from collections.abc import Mapping
from decimal import Decimal

from rest_framework import serializers

from categories.selectors import household_categories
from households.selectors import household_members
from subcategories.selectors import household_subcategories

from .models import DUPLICATE_OPEN_DEBT, Expense, ExpenseDebt

REQUIRED_FIELDS = ('date', 'amount', 'store', 'person', 'category', 'subcategory')
EMPTY_MESSAGE = 'Acest câmp nu poate fi gol.'
EMPTY_ERRORS = {'required': EMPTY_MESSAGE, 'null': EMPTY_MESSAGE, 'blank': EMPTY_MESSAGE}


def with_current(queryset, current_id):
    if current_id is None:
        return queryset
    return queryset | queryset.model.objects.filter(pk=current_id)


class ExpenseDebtSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(required=False)
    debtor_label = serializers.SerializerMethodField()

    class Meta:
        model = ExpenseDebt
        fields = ('id', 'debtor', 'debtor_name', 'debtor_label', 'amount', 'status', 'settled_at')
        read_only_fields = ('status', 'settled_at')
        extra_kwargs = {
            'amount': {'min_value': Decimal('0.01'), 'error_messages': EMPTY_ERRORS},
        }
        validators = []

    def get_debtor_label(self, debt):
        return debt.debtor.username if debt.debtor_id else debt.debtor_name

    def validate(self, attrs):
        has_member = attrs.get('debtor') is not None
        has_name = bool(attrs.get('debtor_name'))
        if has_member == has_name:
            raise serializers.ValidationError({'debtor': 'Alege un membru sau scrie un nume.'})
        return attrs


class SettleDebtSerializer(serializers.Serializer):
    amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal('0.01'),
        error_messages=EMPTY_ERRORS,
    )


class OpenDebtSerializer(ExpenseDebtSerializer):
    expense = serializers.UUIDField(source='expense_id', read_only=True)
    expense_date = serializers.DateField(source='expense.date', read_only=True)
    expense_store = serializers.CharField(source='expense.store', read_only=True)
    expense_amount = serializers.DecimalField(
        source='expense.amount', max_digits=12, decimal_places=2, read_only=True
    )
    payer_name = serializers.CharField(source='expense.person.username', read_only=True)

    class Meta(ExpenseDebtSerializer.Meta):
        fields = (
            *ExpenseDebtSerializer.Meta.fields,
            'expense',
            'expense_date',
            'expense_store',
            'expense_amount',
            'payer_name',
        )


class ExpenseSerializer(serializers.ModelSerializer):
    person_name = serializers.CharField(source='person.username', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    subcategory_name = serializers.CharField(source='subcategory.name', read_only=True)
    debts = ExpenseDebtSerializer(many=True, required=False)

    class Meta:
        model = Expense
        fields = (
            'id',
            'date',
            'amount',
            'store',
            'note',
            'link',
            'person',
            'person_name',
            'category',
            'category_name',
            'subcategory',
            'subcategory_name',
            'debts',
        )
        read_only_fields = ('id',)
        extra_kwargs = {
            **{field: {'error_messages': EMPTY_ERRORS} for field in REQUIRED_FIELDS},
            'amount': {'min_value': Decimal('0.01'), 'error_messages': EMPTY_ERRORS},
        }

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
        self.fields['debts'].child.fields['debtor'].queryset = household_members(
            household_id=household_id
        )

    def to_internal_value(self, data):
        # Un câmp lăsat gol în formular vine ca ''. Îl tratăm ca valoare lipsă (None),
        # ca să primească mesajul „nu poate fi gol”, nu „format greșit” / „număr invalid”.
        if isinstance(data, Mapping):
            data = {**data, **{f: None for f in REQUIRED_FIELDS if data.get(f) == ''}}
        return super().to_internal_value(data)

    def validate(self, attrs):
        # La editare parțială (PATCH) câmpurile netrimise își păstrează valoarea curentă.
        category = attrs.get('category', getattr(self.instance, 'category', None))
        subcategory = attrs.get('subcategory', getattr(self.instance, 'subcategory', None))
        if subcategory.category_id != category.id:
            raise serializers.ValidationError(
                {'subcategory': 'Subcategoria nu aparține categoriei alese.'}
            )
        return attrs

    def validate_link(self, value):
        if value and not value.lower().startswith(('http://', 'https://')):
            raise serializers.ValidationError('Linkul trebuie să înceapă cu http:// sau https://.')
        return value

    def validate_debts(self, debts):
        seen = set()
        for item in debts:
            person = item.get('debtor') or item.get('debtor_name', '').lower()
            if person in seen:
                raise serializers.ValidationError(DUPLICATE_OPEN_DEBT)
            seen.add(person)
        return debts


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
