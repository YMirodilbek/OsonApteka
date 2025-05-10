# # from django.test import TestCase
# from requests.auth import HTTPBasicAuth
# import requests
# # Create your tests here.
# url = "http://93.170.11.10:8088/RM_OPT/hs/online/stock"
# username = "Online"
# password = "cJXGLytPHb3nDNZf5gRh7jzwa"
# response = requests.post(url, auth=HTTPBasicAuth(username, password), stream=True, json={})
# if response.status_code == 200:
#     data = response.json().get('array', [])

# for i in data:
#     print(i)
#     print()
#     print()


# cd /etc/supervisor/conf.d/
# sudo nano celery_admin.conf


# [program:celery_worker]
# command=/home/ubuntu/env/bin/celery -A Admin worker --loglevel=info
# directory=/home/ubuntu/
# user=ubuntu
# autostart=true
# autorestart=true
# stderr_logfile=/var/log/celery_worker.err.log
# stdout_logfile=/var/log/celery_worker.out.log

# [program:celery_beat]
# command=/home/ubuntu/env/bin/celery -A Admin beat --loglevel=info
# directory=/home/ubuntu
# user=ubuntu
# autostart=true
# autorestart=true
# stderr_logfile=/var/log/celery_beat.err.log
# stdout_logfile=/var/log/celery_beat.out.log


# sudo supervisorctl reread
# sudo supervisorctl update
# sudo supervisorctl restart celery_worker
# sudo supervisorctl restart celery_beat
# sudo supervisorctl status


# sudo fallocate -l 2G /swapfile
# sudo chmod 600 /swapfile
# sudo mkswap /swapfile
# sudo swapon /swapfile
# sudo bash -c 'echo "/swapfile none swap sw 0 0" >> /etc/fstab'

# free -h


#  Nima qilish kerak?
# Redis uchun “no-swap” sozlash:
# Redis konfiguratsiyasida vm.overcommit_memory ni sozlang:

# bash

# echo 'vm.overcommit_memory = 1' | sudo tee -a /etc/sysctl.conf
# sudo sysctl -p
# Bu Redis’ga Linux o‘zgaruvchan xotiradan (swap) foydalanmaslikka yordam beradi.

# Redis redis.conf faylida no-appendfsync-on-rewrite yes sozlamasini tekshirib chiqing — diskga yozishdan ogoh bo‘ladi.


# import requests

# url = "http://notify.eskiz.uz/api/auth/login"

# payload={'email': 'marziyahoni@gmail.com',
# 'password': "Aa@9005233"}
# files=[

# ]
# headers = {}

# response = requests.request("POST", url, headers=headers, data=payload, files=files)

# print(response.text)


import requests

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NDkwODkzODYsImlhdCI6MTc0NjQ5NzM4Niwicm9sZSI6InRlc3QiLCJzaWduIjoiZmI1NDQ3N2MwODYyZTM0YTc2Mjk2Yjc0NjcwNGNlNDFiMjJjYjg0ZDExNmIwNWY4ZjE5OTA2YmM4M2NjODc0YSIsInN1YiI6IjEwODE0In0.lDKkNZlcVCuMY9Yh7OmRyrC_bGHDlQJXCwFvRBJfh4w"

url = "https://notify.eskiz.uz/api/message/sms/send"

payload = {
    "mobile_phone": "998951180970",  # raqamni to‘liq formatda yozing
    "message": "Bu Eskiz dan test",
    "from": "4546",  # Eskizda tasdiqlangan sender
    "callback_url": ""  # istasangiz qoldiring
}

headers = {
    'Authorization': f'Bearer {token}'
}

response = requests.post(url, headers=headers, data=payload)
print(response.text)

# access_token = data['data']['token']
# print("TOKEN:", access_token)
