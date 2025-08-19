from django.db.models.signals import post_save
from main.models import Chat, CustomUser
from django.dispatch import receiver
from bs4 import BeautifulSoup
import re


def sanitize_text(text):
    """Matndan HTML teglarni olib tashlab, tozalaydi"""
    if not text:
        return ""

    soup = BeautifulSoup(text, 'html.parser')
    clean_text = soup.get_text(separator='\n')  # <br> lar ham \n bo'ladi

    # Ortga belgilarni tozalash
    clean_text = re.sub(r'[<>]', '', clean_text)
    clean_text = re.sub(r'\n\s*\n', '\n\n', clean_text)  # ketma-ket \n larni kamaytirish
    return clean_text.strip()

def split_text(text, max_length=3000):
    """Uzoq matnni bo‘laklarga ajratish (Telegram uchun foydali)"""
    if len(text) <= max_length:
        return [text]

    parts = []
    while text:
        split_pos = text.rfind('\n', 0, max_length)
        if split_pos == -1:
            split_pos = max_length
        part = text[:split_pos]
        parts.append(part)
        text = text[split_pos:].lstrip()
    return parts



# @receiver(post_save, sender=Chat)
# def notify_chat_new_message(sender, instance, created, **kwargs):
#     if created and instance.is_read == False:
#         user = CustomUser.objects.filter(id=instance.room_id).first()
#         if user and user.onesignal_player_id:
#             unread_count = Chat.objects.filter(room_id=user.id, is_read=False).count()
#             title = "📩 Yangi xabar"
#             body = f"Sizda {unread_count} ta yangi xabar bor"
#             send_onesignal_notification(user.onesignal_player_id, title, body)