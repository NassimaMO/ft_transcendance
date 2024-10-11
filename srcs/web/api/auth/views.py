from rest_framework import generics
from rest_framework.permissions import AllowAny
from .serializers import UserSerializer
from account.models import User

class UserRegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]