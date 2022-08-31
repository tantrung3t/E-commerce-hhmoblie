
from rest_framework import status
from rest_framework import generics
from rest_framework import permissions
from rest_framework_simplejwt import authentication
from rest_framework.views import APIView
from rest_framework.response import Response
from bases.database import order, transaction
from orders.models import Order
from bases.service.stripe import stripe
from bases.exception.exceptions import response_exception
from django.shortcuts import get_object_or_404
from bases.permission.permissions import IsOwnerOrder 


# Create your views here.


class StipeWebhookAPI(APIView):

    def post(self, request):
        event = stripe.stripe_webhook(request)
        if(type(event).__name__ == "SignatureVerificationError"):
            return response_exception(event)
        
        
        if event.type == 'charge.succeeded':
            order_id = event.data.object.metadata.order_id
            order.charge_succeeded(order_id)
            # save transaction if charge success
            transaction.save(event.data.object)
        if event.type == 'charge.failed':
            order_id = event.data.object.metadata.order_id
            order.charge_failed(order_id)
        if event.type == 'charge.refunded':
            order_id = event.data.object.metadata.order_id
            order.charge_refunded(order_id)
            # save transaction if charge refund
            transaction.save(event.data.object)
        return Response(status=status.HTTP_200_OK)


class StipeRefundAPI(APIView):
    authentication_classes = [authentication.JWTAuthentication]
    permission_classes = [IsOwnerOrder]

    def post(self, request):
        check_order = Order.objects.filter(
            id=request.data.get('order_id')
        )
        if not (check_order.exists()):
            return Response(
                data={
                    "message": "not found"
                },
                status=status.HTTP_404_NOT_FOUND
            )
        if(check_order[0].charge_status == "charge_refunded"):
            return Response(
                data={
                    "message": "this order already has been refunded"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        else:
            refund = stripe.stripe_refund(check_order[0].payment_intent)
            return Response(data={
                "message": "refund for this order have success"
            },
                status=status.HTTP_200_OK
            )


class StripeCheckoutAPI(APIView):
    authentication_classes = [authentication.JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        order_id = request.data["order_id"]
        payment_method = request.data["payment_method"]
        order = Order.objects.filter(id = order_id, charge_status = "charge_succeeded")
        if(order.exists()):
            return Response(
                data={"message": "order already has been charge"},
                status=status.HTTP_400_BAD_REQUEST
            )
        payment_intent = stripe.stripe_payment_intent_search(order_id)
        if(payment_intent is None):
            return Response(
                data={"message": "order not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        confirm = stripe.stripe_payment_intent_confirm(
            payment_intent=payment_intent.id,
            payment_method=payment_method
        )
        if(type(confirm).__name__ == "InvalidRequestError"):
            return response_exception(confirm)
        else:
            return Response(data={"message": "checkout for this order success"})


class StripePaymentMethodAPI(generics.ListCreateAPIView):
    authentication_classes = [authentication.JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        stripe_res = stripe.stripe_setup_intent(request)
        return Response(
            data={
                "client_secret": stripe_res.data.client_secret
            })

    def list(self, request, *args, **kwargs):
        stripe_res = stripe.stripe_list_payment_method(request)
        data = []
        for item in stripe_res.data:
            data.append({
                "card_id": item.id,
                "card": {
                    "brand": item.card.brand,
                    "last4": item.card.last4,
                    "exp_month": item.card.exp_month,
                    "exp_year": item.card.exp_year,
                }
            })
        return Response(
            data={
                "object": "list",
                "data": data
            },
            status=status.HTTP_200_OK
        )
