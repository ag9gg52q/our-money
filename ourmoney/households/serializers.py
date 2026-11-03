from django.contrib.auth import get_user_model
from rest_framework import serializers

from . import selectors
from .models import Household


class HouseholdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Household
        fields = ('id', 'name', 'invite_code')
        read_only_fields = ('id', 'invite_code')

    def validate(self, attrs):
        user = self.context['request'].user
        if user.household_id:
            raise serializers.ValidationError('Faci deja parte dintr-o gospodărie.')
        return attrs


class JoinHouseholdSerializer(serializers.Serializer):
    invite_code = serializers.CharField()

    def validate_invite_code(self, value):
        code = value.replace('-', '').replace(' ', '').upper()
        return f'{code[:4]}-{code[4:]}'

    def validate(self, attrs):
        user = self.context['request'].user
        if user.household_id:
            raise serializers.ValidationError('Faci deja parte dintr-o gospodărie.')
        household = Household.objects.filter(invite_code=attrs['invite_code']).first()
        if household is None:
            raise serializers.ValidationError({'invite_code': 'Codul de invitație nu este valid.'})
        attrs['household'] = household
        return attrs


class HouseholdMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('id', 'username', 'first_name', 'last_name', 'role')
        read_only_fields = fields


class HouseholdDetailSerializer(serializers.ModelSerializer):
    invite_code = serializers.SerializerMethodField()
    members = serializers.SerializerMethodField()

    class Meta:
        model = Household
        fields = ('id', 'name', 'invite_code', 'members')
        read_only_fields = ('id',)

    def get_invite_code(self, household):
        if self.context['request'].user.is_admin:
            return household.invite_code
        return None

    def get_members(self, household):
        members = selectors.household_members(household_id=household.id)
        return HouseholdMemberSerializer(members, many=True).data
