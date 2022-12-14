from bases.service.stripe import stripe
from transactions.administrator.serializers import TransactionSerializer


def save(object):
    serializer = TransactionSerializer(data=balance_transaction(object))
    serializer.is_valid(raise_exception=True)
    serializer.save()

def balance_transaction(object):
    try:
        customer = object.metadata.account_id
    except:
        customer = None        
    if(object.refunded):
        balance_transaction = stripe.stripe_transaction(
            object.refunds.data[0].balance_transaction
        )
        data = {
            "timestamp": balance_transaction.created,
            "type": balance_transaction.type,
            "amount": balance_transaction.amount,
            "fee": balance_transaction.fee,
            "net": balance_transaction.net,
            "unit": 100,
            "currency": balance_transaction.currency,
            "order": object.metadata.order_id,
            "customer": customer,
            "payment_id": object.payment_intent,
            "description": "Refund for charge (Payment)"
        }
    else:
        balance_transaction = stripe.stripe_transaction(
            object.balance_transaction
        )
        data = {
            "timestamp": balance_transaction.created,
            "type": balance_transaction.type,
            "amount": balance_transaction.amount,
            "fee": balance_transaction.fee,
            "net": balance_transaction.net,
            "unit": 100,
            "currency": balance_transaction.currency,
            "order": object.metadata.order_id,
            "customer": customer,
            "payment_id": object.payment_intent,
            "description": "Payment success"
        }   
    return data
