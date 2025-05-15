import requests


def send_telegram_message(telegram_id, message):
    token = '7886547250:AAFv0cFJc607ZTRsLHgl_ldRcDGyg5CS9l0'  # BotFatherdan olingan token
    url = f'https://api.telegram.org/bot{token}/sendMessage'
    payload = {
        'chat_id': telegram_id,
        'text': message,
        'parse_mode': 'HTML'
    }
    requests.post(url, data=payload)
    
