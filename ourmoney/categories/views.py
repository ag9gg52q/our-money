from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from households.permissions import IsHouseholdAdminOrReadOnly

from . import selectors, services
from .serializers import CategorySerializer


class CategoryListView(APIView):
    permission_classes = [IsHouseholdAdminOrReadOnly]

    def get(self, request):
        categories = selectors.household_categories(household_id=request.user.household_id)
        return Response(CategorySerializer(categories, many=True).data)

    def post(self, request):
        serializer = CategorySerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        category = services.create_category(
            household_id=request.user.household_id,
            name=serializer.validated_data['name'],
        )
        return Response(CategorySerializer(category).data, status=status.HTTP_201_CREATED)


class CategoryDetailView(APIView):
    permission_classes = [IsHouseholdAdminOrReadOnly]

    def patch(self, request, pk):
        category = get_object_or_404(
            selectors.household_categories(household_id=request.user.household_id), pk=pk
        )
        serializer = CategorySerializer(
            category, data=request.data, partial=True, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        category = services.update_category(category=category, data=serializer.validated_data)
        return Response(CategorySerializer(category).data)
