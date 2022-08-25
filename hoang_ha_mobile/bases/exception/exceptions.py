from rest_framework import status
from rest_framework.response import Response


def response_exception(e):
    return Response(
        data={
            "message": str(e)
        },
        status=status.HTTP_400_BAD_REQUEST
    )
