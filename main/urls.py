from django.urls import path
from .views import *

urlpatterns = [

    #Authenticate
    path('send-otp/', send_otp, name='send_otp'),
    path('verify-otp/', verify_otp, name='verify_otp'),
    path('complete-registration/', complete_registration, name='complete_registration'),
    path('success/', success, name='success'),
    path('logout/',Logout),
    path('blog/',Blog),
]
