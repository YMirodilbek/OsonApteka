import random
import datetime
from .models import OTPCode

def generate_otp(phone_number):
    """ Yangi OTP yaratib, eski kodlarni o‘chiradi """
    OTPCode.objects.filter(phone_number=phone_number).delete() 
    code = random.randint(1000, 9999) 
    OTPCode.objects.create(phone_number=phone_number, code=code, created_at=datetime.datetime.now())
    # print(f"📩 Yangi tasdiqlash kodi: {code}")  
    return code
