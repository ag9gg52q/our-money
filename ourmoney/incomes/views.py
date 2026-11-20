from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from households.permissions import IsHouseholdMember

from . import selectors, services
from .serializers import IncomeFilterSerializer, IncomeSerializer


class IncomeListView(APIView):
    permission_classes = [IsHouseholdMember]

    def get(self, request):
        filters = IncomeFilterSerializer(data=request.query_params)
        filters.is_valid(raise_exception=True)
        incomes = selectors.household_incomes(
            household_id=request.user.household_id, **filters.validated_data
        )
        total = selectors.incomes_total(incomes=incomes)
        return Response(
            {
                'incomes': IncomeSerializer(incomes, many=True, context={'request': request}).data,
                'total': f'{total:.2f}',
            }
        )

    def post(self, request):
        serializer = IncomeSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        income = services.create_income(
            household_id=request.user.household_id, data=serializer.validated_data
        )
        return Response(
            IncomeSerializer(income, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )


class IncomeDetailView(APIView):
    permission_classes = [IsHouseholdMember]

    def patch(self, request, pk):
        income = get_object_or_404(
            selectors.household_incomes(household_id=request.user.household_id), pk=pk
        )

        serializer = IncomeSerializer(
            income, data=request.data, partial=True, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        income = services.update_income(income=income, data=serializer.validated_data)
        return Response(
            IncomeSerializer(income, context={'request': request}).data,
        )

    def delete(self, request, pk):
        income = get_object_or_404(
            selectors.household_incomes(household_id=request.user.household_id), pk=pk
        )
        services.delete_income(income=income)
        return Response(status=status.HTTP_204_NO_CONTENT)
