import requests
from requests.auth import HTTPBasicAuth
url = "http://93.170.11.10:8088/RM_OPT/hs/online/stock/update"
username = "Online"
password = "cJXGLytPHb3nDNZf5gRh7jzwa"
response = requests.post(url, auth=HTTPBasicAuth(username, password), stream=True, json={},)
data = response.json().get('array', [])
print(len(data))