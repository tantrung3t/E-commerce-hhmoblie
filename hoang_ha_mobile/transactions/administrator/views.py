
from rest_framework import status, filters
from rest_framework import generics
from rest_framework_simplejwt import authentication
from rest_framework import permissions
from rest_framework.response import Response
from transactions import models
from .serializers import TransactionReadSerializer


class TransactionAPI(generics.ListAPIView):
    # authentication_classes = [authentication.JWTAuthentication]
    # permission_classes = [permissions.IsAdminUser]
    queryset = models.Transaction.objects.all()
    serializer_class = TransactionReadSerializer
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['timestamp']
    search_fields = ['type', 'currency']