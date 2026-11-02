from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from households.permissions import IsHouseholdAdminOrReadOnly

from . import selectors, services
from .serializers import IncomeSourceSerializer


class IncomeSourceListView(APIView):
    permission_classes = [IsHouseholdAdminOrReadOnly]

    def get(self, request):
        income_sources = selectors.household_income_sources(household_id=request.user.household_id)
        return Response(IncomeSourceSerializer(income_sources, many=True).data)

    def post(self, request):
        serializer = IncomeSourceSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        income_source = services.create_income_source(
            household_id=request.user.household_id,
            name=serializer.validated_data['name'],
        )
        return Response(IncomeSourceSerializer(income_source).data, status=status.HTTP_201_CREATED)


class IncomeSourceDetailView(APIView):
    permission_classes = [IsHouseholdAdminOrReadOnly]

    def patch(self, request, pk):
        income_source = get_object_or_404(
            selectors.household_income_sources(household_id=request.user.household_id), pk=pk
        )
        serializer = IncomeSourceSerializer(
            income_source, data=request.data, partial=True, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        income_source = services.update_income_source(
            income_source=income_source, data=serializer.validated_data
        )
        return Response(IncomeSourceSerializer(income_source).data)
