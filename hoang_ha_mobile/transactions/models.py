from sqlite3 import Timestamp
from django.db import models
from django.contrib.auth import get_user_model
from orders.models import Order
# Create your models here.

User = get_user_model()

TYPE = [
    ("charge", "Charge"),
    ("refund", "Refund")
]

class Transaction(models.Model):
    timestamp = models.CharField(max_length=15)
    type = models.CharField(choices=TYPE, max_length=50)
    amount = models.BigIntegerField()
    fee = models.BigIntegerField(default=0)
    net = models.BigIntegerField()
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    customer = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    payment_id = models.CharField(max_length=50)
    description = models.CharField(max_length=255)

    class Meta:
        db_table = 'transactions' 
 