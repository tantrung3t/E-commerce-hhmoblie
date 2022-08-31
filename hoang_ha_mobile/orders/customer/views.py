from rest_framework import generics, permissions, response, status, views
from rest_framework_simplejwt import authentication
from bases.service.stripe.stripe import stripe_payment_intent_create
from bases.service.stripe.stripe import stripe_payment_intent_confirm
from bases.service.stripe.stripe import stripe_customer_create
from bases.service.fcm.notification import fcm_send
from hoang_ha_mobile.base.errors import check_valid_item
from variants.models import Variant
from . import serializers
from .. import models


class ListCreateOrderAPIView(generics.ListCreateAPIView):
    authentication_classes = [authentication.JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.OrderReadSerializer

    def get_queryset(self):
        self.queryset = models.Order.objects.filter(
            created_by=self.request.user.id)
        return super().get_queryset()

    def post(self, request, *args, **kwargs):
        serializer = serializers.OrderSerializer(
            data=request.data.get('order'))
        array_order_detail = self.request.data.get("order_details")
        check_items = check_valid_item(array_order_detail)
        if(check_items is not None):
            return check_items
        if(serializer.is_valid()):
            self.instance = serializer.save(created_by=self.request.user)
            total_price = 0
            for order_detail in array_order_detail:
                variant = Variant.objects.get(id=order_detail.get('variant'))
                if(variant.sale > 0):
                    price = variant.sale
                else:
                    price = variant.price
                total_price += int(price) * int(order_detail.get('quantity'))
                data = {
                    "order": self.instance.id,
                    "variant": order_detail.get('variant'),
                    "quantity": order_detail.get('quantity'),
                    "price": price
                }
                serializer = serializers.OrderDetailSerializer(data=data)
                if(serializer.is_valid()):
                    serializer.save()
            self.instance.total = total_price
            
            serializer = serializers.OrderSerializer(self.instance)
            if self.request.user.stripe_customer_id is None:
                stripe_customer = stripe_customer_create(self.request.user)
                self.request.user.stripe_customer_id = stripe_customer
                self.request.user.save()
            else:
                stripe_customer = self.request.user.stripe_customer_id
            res = stripe_payment_intent_create(
                order=self.instance.id,
                amount=total_price,
                user=self.request.user.id,
                customer=stripe_customer,
                payment_method=None
            )
            self.instance.payment_intent = res.data.id
            self.instance.save()
            if(res.status_code == 400):
                return response.Response(data=res.data, status=status.HTTP_400_BAD_REQUEST)
            confirm_payment = stripe_payment_intent_confirm(
                res.data.id, request.data.get('payment_method'))
            if(confirm_payment.status_code == 400):
                data = {
                    "message": confirm_payment.data['message'],
                    "charge": False,
                    "orders": serializer.data
                }
                return response.Response(data=data, status=status.HTTP_201_CREATED)
            fcm_send("New Order", "You have a new order")
            data = {
                "message": "order success",
                "charge": True,
                "orders": serializer.data
            }
            return response.Response(data=data, status=status.HTTP_201_CREATED)
        else:
            return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
