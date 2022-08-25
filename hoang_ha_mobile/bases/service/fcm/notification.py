import os
import json
import requests
from devices import models
from dotenv import load_dotenv
load_dotenv()


def send_notification(registration_ids, message_title, message_desc):
    fcm_api = os.getenv('FCM_API_KEY')
    url = "https://fcm.googleapis.com/fcm/send"
    headers = {
        "Content-Type": "application/json",
        "Authorization": 'key='+fcm_api
    }
    payload = {
        "registration_ids": registration_ids,
        "priority": "high",
        "notification": {
            "body": message_desc,
            "title": message_title,
            "image": "https://world.com"
        }
    }
    # send request to Firebase Cloud Messaging
    requests.post(url, data=json.dumps(payload), headers=headers)


def fcm_send():
    # get device token of admin account
    token = models.Token.objects.get(
        user_id='5feec0fc-a836-4d93-b09e-26f966567d53')
    registration = [token.token_device]
    # call function
    send_notification(registration, "Order", "Have 1 order created")
