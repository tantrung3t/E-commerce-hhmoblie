import os
import stripe
from dotenv import load_dotenv
from rest_framework import status
from rest_framework.response import Response
from bases.exception.exceptions import response_exception

load_dotenv()
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')


def stripe_customer_create(user):  # function created stripe customer
    try:
        customer = stripe.Customer.create(
            email=user.email,
            name=user.full_name
        )
    except Exception as e:
        return None
    return customer.id


def stripe_customer_search(user):  # function search stripe customer
    customer = stripe.Customer.search(
        query="email:'%s'" % (user.email),
    )
    if(len(customer.data) == 0):
        customer_id = stripe_customer_create(user)
    else:
        customer_id = customer.data[0].id
    return customer_id


def stripe_payment_intent_create(order_id, amount, user):  # create PaymentIntent
    customer = stripe_customer_search(user)
    try:
        payment = stripe.PaymentIntent.create(
            amount=amount,
            currency="usd",
            payment_method_types=['card'],
            description="Payment",
            metadata={
                "order_id": order_id,
                "account_id": user.id
            },
            customer=customer
        )
    except Exception as e:
        return response_exception(e)
    return Response(data=payment)


# confirm PaymentIntent
def stripe_payment_intent_confirm(payment_intent, payment_method):
    try:
        confirm = stripe.PaymentIntent.confirm(
            payment_intent,
            payment_method=payment_method,
        )
    except Exception as e:
        return e
    return confirm


# Function listen event from Stripe
def stripe_webhook(request):
    endpoint_secret = os.getenv('ENDPOINT_SECRET')
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    # Check valid payload with signature
    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=sig_header,
            secret=endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return e
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return e
    return event


def stripe_setup_intent(request):
    try:
        setup = stripe.SetupIntent.create(
            payment_method_types=["card"],
            customer=stripe_customer_search(request.user)
        )
    except Exception as e:
        return response_exception(e)
    return Response(data=setup)


def stripe_list_payment_method(request):
    try:
        payment_methods = stripe.Customer.list_payment_methods(
            stripe_customer_search(request.user),
            type="card",
        )
    except Exception as e:
        return response_exception(e)
    return Response(data=payment_methods)


def stripe_payment_intent_search(order_id):
    try:
        payment_intent = stripe.PaymentIntent.search(
            query="metadata['order_id']:'%s'" % (order_id),
        )
    except Exception as e:
        print(e)
        return response_exception(e)
    if(len(payment_intent.data) == 0):
        payment_intent = None
    else:
        payment_intent = payment_intent.data[0]
    return payment_intent


# print(stripe_payment_intent_search(90).charges.data[0].id)
def stripe_refund(charge):
    try:
        refund = stripe.Refund.create(
            charge=charge,
        )
    except Exception as e:
        return e
    return refund


def stripe_transaction(txn):
    try:
        transaction = stripe.BalanceTransaction.retrieve(
            txn,
        )
    except Exception as e:
        return e
    return transaction
