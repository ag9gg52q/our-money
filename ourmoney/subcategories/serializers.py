from rest_framework import serializers

from .models import Subcategory


class SubcategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Subcategory
        fields = ('id', 'name', 'is_active')
        read_only_fields = ('id',)

    def validate_name(self, value):
        category = self.context['category']
        duplicates = category.subcategories.filter(name__iexact=value)
        if self.instance is not None:
            duplicates = duplicates.exclude(pk=self.instance.pk)
        if duplicates.exists():
            raise serializers.ValidationError(
                'Există deja o subcategorie cu acest nume în categorie.'
            )
        return value
