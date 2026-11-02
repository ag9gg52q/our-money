from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from categories.selectors import household_categories
from households.permissions import IsHouseholdAdminOrReadOnly

from . import selectors, services
from .serializers import SubcategorySerializer


def get_household_category(request, category_id):
    return get_object_or_404(
        household_categories(household_id=request.user.household_id), pk=category_id
    )


class SubcategoryListView(APIView):
    permission_classes = [IsHouseholdAdminOrReadOnly]

    def get(self, request, category_id):
        category = get_household_category(request, category_id)
        subcategories = category.subcategories.all()
        return Response(SubcategorySerializer(subcategories, many=True).data)

    def post(self, request, category_id):
        category = get_household_category(request, category_id)
        serializer = SubcategorySerializer(data=request.data, context={'category': category})
        serializer.is_valid(raise_exception=True)
        subcategory = services.create_subcategory(
            category_id=category.id,
            name=serializer.validated_data['name'],
        )
        return Response(SubcategorySerializer(subcategory).data, status=status.HTTP_201_CREATED)


class SubcategoryDetailView(APIView):
    permission_classes = [IsHouseholdAdminOrReadOnly]

    def patch(self, request, pk):
        subcategory = get_object_or_404(
            selectors.household_subcategories(household_id=request.user.household_id), pk=pk
        )
        serializer = SubcategorySerializer(
            subcategory, data=request.data, partial=True, context={'category': subcategory.category}
        )
        serializer.is_valid(raise_exception=True)
        subcategory = services.update_subcategory(
            subcategory=subcategory, data=serializer.validated_data
        )
        return Response(SubcategorySerializer(subcategory).data)
