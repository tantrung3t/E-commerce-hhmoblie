from ast import Or
from orders.models import Order
from rest_framework import serializers


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            'charge_status',
        ]


def db_update(order_id, status):
    queryset = Order.objects.get(id=order_id)
    serializer = OrderSerializer(queryset, data={"charge_status": status})
    serializer.is_valid(raise_exception=True)
    serializer.save()


def order_created(order_id):
    print("order_created")


def charge_succeeded(order_id):
    db_update(order_id, "charge_succeeded")


def payment_failed(order_id):
    db_update(order_id, "payment_failed")


def charge_refunded(order_id):
    db_update(order_id, "charge_refunded")
