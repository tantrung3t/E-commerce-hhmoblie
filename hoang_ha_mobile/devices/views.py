from rest_framework import views, generics
from rest_framework.response import Response
from rest_framework import status
from .models import Token
from .serializers import TokenSerializer
# Create your views here.

class DeviceTokenAPI(generics.CreateAPIView):
    queryset = Token.objects.all()
    serializer_class = TokenSerializer
    