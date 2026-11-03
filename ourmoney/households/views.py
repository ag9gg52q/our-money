from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from . import selectors, services
from .permissions import IsHouseholdAdminOrReadOnly
from .serializers import (
    HouseholdDetailSerializer,
    HouseholdMemberSerializer,
    HouseholdSerializer,
    JoinHouseholdSerializer,
)


class HouseholdCreateView(APIView):
    def post(self, request):
        serializer = HouseholdSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        household = services.create_household(
            user=request.user, name=serializer.validated_data['name']
        )
        return Response(HouseholdSerializer(household).data, status=status.HTTP_201_CREATED)


class HouseholdJoinView(APIView):
    def post(self, request):
        serializer = JoinHouseholdSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        household = services.join_household(
            user=request.user, household=serializer.validated_data['household']
        )
        return Response({'id': household.id, 'name': household.name}, status=status.HTTP_200_OK)


class CurrentHouseholdView(APIView):
    permission_classes = [IsHouseholdAdminOrReadOnly]

    def get(self, request):
        serializer = HouseholdDetailSerializer(request.user.household, context={'request': request})
        return Response(serializer.data)

    def patch(self, request):
        household = request.user.household
        serializer = HouseholdDetailSerializer(
            household, data=request.data, partial=True, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        household = services.update_household(
            household=household, name=serializer.validated_data.get('name', household.name)
        )
        return Response(HouseholdDetailSerializer(household, context={'request': request}).data)


class MakeAdminView(APIView):
    permission_classes = [IsHouseholdAdminOrReadOnly]

    def post(self, request, pk):
        member = get_object_or_404(
            selectors.household_members(household_id=request.user.household_id), pk=pk
        )
        services.make_admin(member=member)
        return Response(HouseholdMemberSerializer(member).data)
