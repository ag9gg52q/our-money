from rest_framework import serializers

from .models import Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'is_active')
        read_only_fields = ('id',)

    def validate_name(self, value):
        household_id = self.context['request'].user.household_id
        duplicates = Category.objects.filter(household_id=household_id, name__iexact=value)
        if self.instance is not None:
            duplicates = duplicates.exclude(pk=self.instance.pk)
        if duplicates.exists():
            raise serializers.ValidationError(
                'Există deja o categorie cu acest nume în gospodărie.'
            )
        return value
