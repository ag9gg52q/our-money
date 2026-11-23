from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from households.permissions import IsHouseholdAdmin

from . import selectors, services
from .serializers import SavingsEntrySerializer


class SavingsEntryListView(APIView):
    permission_classes = [IsHouseholdAdmin]

    def get(self, request):
        savings_entry = selectors.household_savings_entries(household_id=request.user.household_id)
        summary = selectors.savings_summary(household_id=request.user.household_id)
        return Response(
            {
                'savings_entries': SavingsEntrySerializer(
                    savings_entry, many=True, context={'request': request}
                ).data,
                'balance': f'{summary["balance"]:.2f}',
                'deposits': f'{summary["deposits"]:.2f}',
                'withdrawals': f'{summary["withdrawals"]:.2f}',
            }
        )

    def post(self, request):
        serializer = SavingsEntrySerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        savings_entry = services.create_savings_entry(
            household_id=request.user.household_id, data=serializer.validated_data
        )
        return Response(
            SavingsEntrySerializer(savings_entry, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )


class SavingsEntryDetailView(APIView):
    permission_classes = [IsHouseholdAdmin]

    def patch(self, request, pk):
        savings_entry = get_object_or_404(
            selectors.household_savings_entries(household_id=request.user.household_id), pk=pk
        )

        serializer = SavingsEntrySerializer(
            savings_entry, data=request.data, partial=True, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        savings_entry = services.update_savings_entry(
            savings_entry=savings_entry, data=serializer.validated_data
        )
        return Response(
            SavingsEntrySerializer(savings_entry, context={'request': request}).data,
        )

    def delete(self, request, pk):
        savings_entry = get_object_or_404(
            selectors.household_savings_entries(household_id=request.user.household_id), pk=pk
        )
        services.delete_savings_entry(savings_entry=savings_entry)
        return Response(status=status.HTTP_204_NO_CONTENT)
