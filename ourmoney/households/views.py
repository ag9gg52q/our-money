from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from . import services
from .serializers import HouseholdSerializer, JoinHouseholdSerializer


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
