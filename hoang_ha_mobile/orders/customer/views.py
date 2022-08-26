from rest_framework import generics, permissions, response, status, views
from rest_framework_simplejwt import authentication
from hoang_ha_mobile.base.errors import check_valid_item
from bases.service.stripe.stripe import stripe_payment_intent_create
from bases.service.stripe.stripe import stripe_payment_intent_confirm
from bases.service.fcm.notification import fcm_send
from variants.models import Variant
from . import serializers
from .. import models
class ListCreateOrderAPIView(generics.ListCreateAPIView):
    authentication_classes = [authentication.JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.OrderReadSerializer
    
    def get_queryset(self):        
        self.queryset = models.Order.objects.filter(created_by=self.request.user.id)
        return super().get_queryset()    
    
    def post(self, request, *args, **kwargs):
        serializer = serializers.OrderSerializer(data=request.data.get('order'))   
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
            self.instance.save()
            res = stripe_payment_intent_create(self.instance.id, total_price, self.request.user)
            serializer = serializers.OrderSerializer(self.instance)
            fcm_send("New Order", "You have a new order")
            return response.Response(data=serializer.data, status=status.HTTP_201_CREATED)
        else:
            return response.Response(serializer.errors, status= status.HTTP_400_BAD_REQUEST)
