from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from matchmaker.models import MatchChoice
from .serializers import MatchChoiceSerializer

class MatchChoiceView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        serializer = MatchChoiceSerializer(data=request.data)
        if serializer.is_valid():
            match_choice = serializer.save()
            return Response({
                'match_choice_id': match_choice.id,
                'matchmaking': match_choice.need_matchmaking()
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
