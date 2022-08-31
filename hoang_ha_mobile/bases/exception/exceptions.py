from rest_framework import status
from rest_framework.response import Response


def response_exception(message):
    return Response(
        data = {
            "message": str(message)
        },
        status = status.HTTP_400_BAD_REQUEST
    )
