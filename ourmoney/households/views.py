from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from . import services
from .serializers import HouseholdSerializer


class HouseholdCreateView(APIView):
    def post(self, request):
        serializer = HouseholdSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        household = services.create_household(
            user=request.user, name=serializer.validated_data['name']
        )
        return Response(HouseholdSerializer(household).data, status=status.HTTP_201_CREATED)
