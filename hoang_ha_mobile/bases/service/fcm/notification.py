
import os
import firebase_admin
from devices import models
from firebase_admin import credentials, messaging
from django.contrib.auth import get_user_model
from devices.serializers import TokenSerializer

User = get_user_model()

# setup credential for firebase
credential_json_path = str(os.path.dirname(
    os.path.abspath(__file__))) + r'\serviceAccountKey.json'
cred = credentials.Certificate(credential_json_path)
firebase_admin.initialize_app(cred)


# function push notification fcm
def sendPush(title, msg, registration_token, dataObject=None):
    message = messaging.MulticastMessage(
        notification=messaging.Notification(
            title=title,
            body=msg
        ),
        data=dataObject,
        tokens=registration_token
    )
    messaging.send_multicast(message)


def fcm_send():
    # get device token of admin account
    token = models.Token.objects.filter(user_id__is_superuser=True)
    token_serializer = TokenSerializer(token, many=True)
    registration = []
    # add device token into list
    for x in range(len(token)):
        registration.append(token_serializer.data[x]['token_device'])
    # call function sendPush to push notification
    sendPush("New order", "You have 1 order", registration)
