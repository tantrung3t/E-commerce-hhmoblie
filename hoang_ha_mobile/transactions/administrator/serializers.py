
from dataclasses import fields
from rest_framework import serializers
from transactions import models
from django.contrib.auth import get_user_model
User = get_user_model()
class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Transaction
        fields = [
            "id",
            "timestamp",
            "type",
            "amount",
            "fee",
            "net",
            "unit",
            "currency",
            "payment_id",
            "description",
            "order",
            "customer"
        ]

class ShortCustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "full_name"
        ]

class TransactionReadSerializer(serializers.ModelSerializer):
    customer = ShortCustomerSerializer()
    class Meta:
        model = models.Transaction
        fields = [
            "id",
            "timestamp",
            "type",
            "amount",
            "fee",
            "net",
            "unit",
            "currency",
            "payment_id",
            "description",
            "order",
            "customer"
        ]