from rest_framework import serializers

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
