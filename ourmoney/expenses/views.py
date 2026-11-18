from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from households.permissions import IsHouseholdMember

from . import selectors, services
from .serializers import ExpenseFilterSerializer, ExpenseSerializer


class ExpenseListView(APIView):
    permission_classes = [IsHouseholdMember]

    def get(self, request):
        filters = ExpenseFilterSerializer(data=request.query_params)
        filters.is_valid(raise_exception=True)
        expenses = selectors.household_expenses(
            household_id=request.user.household_id, **filters.validated_data
        )
        total = selectors.expenses_total(expenses=expenses)
        return Response(
            {
                'expenses': ExpenseSerializer(
                    expenses, many=True, context={'request': request}
                ).data,
                'total': f'{total:.2f}',
            }
        )

    def post(self, request):
        serializer = ExpenseSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        expense = services.create_expense(
            household_id=request.user.household_id, data=serializer.validated_data
        )
        return Response(
            ExpenseSerializer(expense, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )


class ExpenseDetailView(APIView):
    permission_classes = [IsHouseholdMember]

    def patch(self, request, pk):
        expense = get_object_or_404(
            selectors.household_expenses(household_id=request.user.household_id), pk=pk
        )

        serializer = ExpenseSerializer(
            expense, data=request.data, partial=True, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        expense = services.update_expense(expense=expense, data=serializer.validated_data)
        return Response(
            ExpenseSerializer(expense, context={'request': request}).data,
        )

    def delete(self, request, pk):
        expense = get_object_or_404(
            selectors.household_expenses(household_id=request.user.household_id), pk=pk
        )
        services.delete_expense(expense=expense)
        return Response(status=status.HTTP_204_NO_CONTENT)
