from rest_framework.decorators import api_view,  permission_classes
from rest_framework.permissions import  AllowAny, IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.db.models import Sum, F, Prefetch, Count, Q
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import render 
from rest_framework import viewsets
from rest_framework import status
from main.views import send_sms
from . serilalizer import *
from main.models import *
import random
import redis
import re


r = redis.Redis(host='localhost', port=6379, db=0)

@api_view(['POST'])
def phone_number_api(request):
    try:
        phone_number = request.data.get('phone', '')
        phone_number = re.sub(r'\D', '', phone_number)
        if phone_number.startswith("998") and len(phone_number) == 12:
            pass
        elif phone_number.startswith("9") and len(phone_number) == 9:
            phone_number = "998" + phone_number
        elif phone_number.startswith("0") and len(phone_number) == 10:
            phone_number = "998" + phone_number[1:]
        else:
            return Response({"status": 400, "message": "Telefon raqami noto‘g‘ri formatda"}, status=status.HTTP_400_BAD_REQUEST)
        otp = random.randint(1000, 9999)
        
        r.setex(f"otp_{str(otp)}", 50000 ,phone_number ) 

        success = send_sms(phone_number, otp)
        if not success:
            return Response({"status": 500, "message": "SMS yuborishda xatolik"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"status": 200, "message": "OTP yuborildi",}, status=status.HTTP_200_OK)

    except Exception as e:

        return Response({"status": 500, "message": f"Server xatosi: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def login_api( request):
    otp = request.data.get('otp')
    if not otp:
        return Response({'success': False, 'message': 'OTP kiritilmagan'}, status=status.HTTP_400_BAD_REQUEST)

    phone = r.get(f"otp_{otp}")
    if not phone:
        return Response({'success': False, 'message': 'OTP noto‘g‘ri yoki vaqti tugagan'}, status=status.HTTP_400_BAD_REQUEST)
    phone = phone.decode()
    user, created = CustomUser.objects.get_or_create(
        phone_number=phone,
        defaults={'is_agree': True}
    )

    if not created:
        user.is_agree = True
        user.save()

    token, _ = Token.objects.get_or_create(user=user)
    
    r.delete(f"otp_{otp}")

    return Response({
        'success': True,
        'token': token.key,
        'user': {
            'id': user.id,
            'phone_number': user.phone_number,
            'is_agree': user.is_agree,
        }
    })


@api_view(["GET"])
# @permission_classes([IsAuthenticated])
def get_category(request):
    category = Category.objects.all()
    serializer = CategorySerializer(category, many=True )
    return Response(serializer.data)


@api_view(["GET"])
# @permission_classes([IsAuthenticated])
def category(request, pk):
    category = Category.objects.get(id=pk)
    serializer = CategorySerializer(category, many=False )
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user(request):
    user = request.user
    serializer = UserSerializer(user, many = False)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def user_update(request):
    user = request.user
    user.first_name = request.data['first_name']
    user.last_name = request.data['last_name']
    user.save()
    return Response(UserSerializer(user, many= False).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_dastafca(request):
    dastafca = Dostafca.objects.last()
    return Response(DastafcaSerializer(dastafca, many=False).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_filial(request):
    filial = Filial.objects.all()
    return Response (FilialSerializer(filial, many=True).data)