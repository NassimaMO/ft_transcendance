from rest_framework import status
from rest_framework.response import Response
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from account.models import User
import logging

logger = logging.getLogger('default')


def check_user(**kwargs):
    """Helper to centralize user checking"""

    user_id = kwargs.get("user_id")
    username = kwargs.get("username")
    request_status = status.HTTP_404_NOT_FOUND
    user_message = ''
    error = ''
    if user_id:
        try:
            user = User.objects.get(id=user_id)
        except Exception:
            user = None
        user_message = f"with id {user_id}"
    elif username:
        try:
            user = User.objects.get(username=username)
        except Exception:
            user = None
        user_message = f"with username {username}"
    else:
        user = None
        error = ": Missing or invalid identifier"
        request_status = status.HTTP_400_BAD_REQUEST
    if not user:
        message = {
            "errors": {
                "unknown_user": f"User {user_message} not found {error}"
                }
            }
        return {"user": None, "error_response": Response(message, status=request_status)}
    return {"user": user, "user_message": user_message}


def send_ws_message(recipient_type, recipient_id, message_type, **extra) :
    message = {
            "type": message_type,
            **extra
        }
    group_name = f"{recipient_type}_{recipient_id}"
    logger.info(f"sending message to {group_name} : {message}")
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        group_name,
        message
    )


def send_notifications(recipient_type, recipient_id, *changes):
    """Helper to send channel notifications"""

    send_ws_message(recipient_type, recipient_id, "api_notif", changes=changes)