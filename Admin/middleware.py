import time
from django.http import HttpResponseForbidden

# IP'lar saqlanadigan vaqtinchalik xotira (memory)
BLOCKED_IPS = {}
REQUEST_COUNT = {}

BLOCK_DURATION = 60 * 5   # 5 daqiqa blok
MAX_REQUESTS = 50          # 50 ta so‘rovdan oshsa blok
TIME_WINDOW = 60           # 60 soniya ichida

class IPBlockMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip = self.get_client_ip(request)
        now = time.time()

        # Agar IP blokda bo‘lsa
        if ip in BLOCKED_IPS and now < BLOCKED_IPS[ip]:
            return HttpResponseForbidden("❌ Sizning IP manzilingiz vaqtincha bloklangan.")

        # So‘rovlarni hisoblash
        self.track_requests(ip, now)

        return self.get_response(request)

    def track_requests(self, ip, now):
        # Eski ma’lumotlarni tozalaymiz
        REQUEST_COUNT.setdefault(ip, [])
        REQUEST_COUNT[ip] = [t for t in REQUEST_COUNT[ip] if now - t < TIME_WINDOW]
        REQUEST_COUNT[ip].append(now)

        # Chegaradan oshsa, bloklaymiz
        if len(REQUEST_COUNT[ip]) > MAX_REQUESTS:
            BLOCKED_IPS[ip] = now + BLOCK_DURATION
            print(f"🚫 IP bloklandi: {ip} ({BLOCK_DURATION/60} daqiqa)")

    def get_client_ip(self, request):
        # Proxy yoki nginx ortidan IP olish
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
