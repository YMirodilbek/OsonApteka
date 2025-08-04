from django.shortcuts import  redirect
from django.http import JsonResponse
from main.models import CustomUser
from django.conf import settings
from functools import wraps
import requests

def is_staff(fun):
    @wraps(fun)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_staff:
            return fun(request, *args, **kwargs)
        return redirect( '/filial/login/')
    return wrapper

def login_required_ajax(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({"status": 401, "message": "Unauthorized"}, status=401)
        return view_func(request, *args, **kwargs)
    return wrapper


def send_onesignal_notification(player_id, title, message):
    onsignal_key = settings.ONSIGNAL_KEY
    url = "https://onesignal.com/api/v1/notifications"
    payload = {
        "app_id": "5e8f2bf1-bb90-4147-bc04-d6ce758de977",  # Sizning OneSignal App ID'ingiz
        "include_player_ids": [player_id],
        "headings": {"en": title},
        "contents": {"en": message}
    }
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": f"Basic {onsignal_key}"
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.status_code, response.json()


def send_chat_notification_if_needed(chat_instance):
    user = CustomUser.objects.filter(id=chat_instance.room_id).first()
    if user and user.onesignal_player_id:
        unread_count = Chat.objects.filter(room_id=user.id, is_read=False).count()
        title = "📩 Yangi xabar"
        body = f"Sizda {unread_count} ta yangi xabar bor"
        send_onesignal_notification(user.onesignal_player_id, title, body)