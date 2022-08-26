
from rest_framework import status
from rest_framework import generics
from rest_framework import permissions
from rest_framework_simplejwt import authentication
from rest_framework.views import APIView
from rest_framework.response import Response
from bases.database import order, transaction
from bases.service.stripe import stripe
from bases.exception.exceptions import response_exception
from orders.models import Order


# Create your views here.


class StipeWebhookAPI(APIView):

    def post(self, request):
        event = stripe.stripe_webhook(request)
        if(type(event).__name__ == "SignatureVerificationError"):
            return response_exception(event)
        if event.type == 'setup_intent.created':
            return Response(status=status.HTTP_200_OK)
        order_id = event.data.object.metadata.order_id
        if event.type == 'payment_intent.created':
            order.order_created(order_id)
        if event.type == 'charge.succeeded':
            order.charge_succeeded(order_id)
            # save transaction if charge success
            transaction.save(event.data.object)
        if event.type == 'payment_intent.payment_failed':
            order.payment_failed(order_id)
        if event.type == 'charge.refunded':
            order.charge_refunded(order_id)
            # save transaction if charge refund
            transaction.save(event.data.object)
        return Response(status=status.HTTP_200_OK)


class StipeRefundAPI(APIView):
    authentication_classes = [authentication.JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        check_order = Order.objects.get(id=request.data.get('order_id'))
        if(check_order.status == 'processing'):
            payment_intent = stripe.stripe_payment_intent_search(
                request.data['order_id'])
            refund = stripe.stripe_refund(payment_intent.charges.data[0].id)
            if(type(refund).__name__ == "InvalidRequestError"):
                return response_exception(refund)
            else:
                return Response(data=refund)
        else:
            return Response(
                data={
                    "message": "can't refund for this order"
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class StripeCheckoutAPI(APIView):
    authentication_classes = [authentication.JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        order_id = request.data["order_id"]
        payment_method = request.data["payment_method"]
        payment_intent = stripe.stripe_payment_intent_search(order_id)
        if(payment_intent is None):
            return Response(
                data={"message": "order_id not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        confirm = stripe.stripe_payment_intent_confirm(
            payment_intent=payment_intent.id,
            payment_method=payment_method
        )
        if(type(confirm).__name__ == "InvalidRequestError"):
            return response_exception(confirm)
        else:
            return Response(data=confirm)


class StripePaymentMethodAPI(generics.ListCreateAPIView):
    authentication_classes = [authentication.JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        return stripe.stripe_setup_intent(request)

    def list(self, request, *args, **kwargs):
        return stripe.stripe_list_payment_method(request)
