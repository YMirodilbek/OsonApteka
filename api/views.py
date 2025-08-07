from rest_framework.decorators import api_view,  permission_classes
from rest_framework.permissions import  AllowAny, IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Sum, F, Prefetch, Count, Q
from main.bot_messages import send_telegram_message
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from rest_framework.response import Response
from tmp.models import Landlord, Applicant
from rest_framework.views import APIView
from django.utils.timezone import now
from django.shortcuts import render 
from rest_framework import viewsets
from rest_framework import status
from django.conf import settings
from main.views import send_sms
from click_up import ClickUp
from decimal import Decimal
from . serilalizer import *
from main.models import *
import random
import redis
import re
import logging
r = redis.Redis(host='localhost', port=6379, db=0)

class ApplicantApiView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        data = request.data
        serializer = ApplicantSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({'success':True})
        return Response({'success':False, 'errors': serializer.errors})

class LandlordApiView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        data = request.data
        serializer = LandlordSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({'success':True})
        return Response({'success':False, 'errors': serializer.errors})  
        

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


class LoginAPIView(APIView):
    def post(self, request):
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

        refresh = RefreshToken.for_user(user)

        r.delete(f"otp_{otp}")

        return Response({
            'success': True,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
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
# @permission_classes([IsAuthenticated])
def get_dastafca(request):
    dastafca = Dostafca.objects.last()
    return Response(DastafcaSerializer(dastafca, many=False).data)


@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def get_filial(request):
    filial = Filial.objects.all()
    return Response (FilialSerializer(filial, many=True).data)



@api_view(['GET'])
def product_order(request):
    products_id = (
    OrderItem.objects
    .values('product_id')  
    .annotate(total_quantity=Sum('quantity')) 
    .order_by('-total_quantity')[:10]  
    .values_list('product_id', flat=True) 
    )
    product = Product.objects.filter(id__in=products_id)
    return Response(
        ProductSerializer(product, many=True).data
    )


@api_view(['GET'])
def get_person_status(request):
    return Response([{'name': i[1]} for i in Product.PERSON_CHOICES])

@api_view(['GET'])
def person(request,*args,**kwargs):
        person_type = request.GET.get('person', None)
        if person_type is not None:
            product_price_qs = ProductPrice.objects.filter(price__gt=0, amount__gt=0)
            products = Product.objects.filter(
            product_prise__in=product_price_qs,
            name__isnull=False,
            category_person = person_type
            ).exclude(name='').order_by('id').distinct().select_related('category','member').prefetch_related(
            Prefetch('product_prise', queryset=product_price_qs, to_attr='prices')
             )
            return Response(
                ProductSerializer(
                    products, many=True
                ).data
            )
        return Response({
            "product":"None"
        })        


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_onesignal_id(request):
    player_id = request.data.get('player_id')
    if player_id:
        request.user.onesignal_player_id = player_id
        request.user.save()
        return Response({'success': True})
    return Response({'success': False, 'message': 'player_id required'})
   
logger = logging.getLogger('Product')

class CheckoutAPIView(APIView):
    permission_classes = [IsAuthenticated] 
    def post(self, request):
        user = request.user
        payment_method = request.data.get('payment_method')
        order = Order.objects.filter(user=user, is_completed=False).first()
        if not order or not order.items.exists():
            return Response({"detail": "Sizning savatingiz bo'sh!"}, status=status.HTTP_400_BAD_REQUEST)

        
        serializer = CheckoutSerializer(instance=order, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(user=user) 
            # address_type = request.data.get('address_type')

            if payment_method == 'card':
                card = VirtualCard.objects.get(user=user)
                order.payment_method = payment_method
                if  card.balance >= Decimal(order.total_price):
                    card.balance -= Decimal(order.total_price)
                    card.save()
                    order.is_paid = True
                    order.is_completed = True
                    order.save()
                    # 📩 Telegramga yuborish
                    telegram_ids = order.filial.users.values_list('telegram_id', flat=True)
                    for tg_id in telegram_ids:
                        send_telegram_message(
                            telegram_id=tg_id,
                            message=f"🆔 ид: {order.id}\n"
                                    f"⏰ соат : {now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                                    f"🏢 филиал : {order.filial}\n"
                                    f"💰 сумма: {order.total_price} сум\n"
                                    f"📞 тел: {order.phone_number1}\n"
                                    f"💊 дорилар сони: {order.items.count()} та\n"
                                    f"📍 Адрес: {order.address_text} \n"
                                    f"💳 тўлов : {'бажарилди' if order.is_paid else 'кутиламоқда'}"
                                    "test: bu test tel qilmang "
                                    )
                    # logger.info(f"Order {order_id} marked as paid successfully")

                    return Response({"success": True, "message": "Buyurtma rasmiylashtirildi", "order_id": order.id}, status=status.HTTP_200_OK)
                
                return Response({"success": False})
                    
            if payment_method == 'click':
                order.payment_method = payment_method
                order.save()
                click = ClickUp(
                    service_id=settings.CLICK_SERVICE_ID,
                    merchant_id=settings.CLICK_MERCHANT_ID
                )
                return_url = request.build_absolute_uri(f'/payment/success/{order.id}/')
                pay_link = click.initializer.generate_pay_link(
                    id=order.id,
                    amount=order.amount,
                    return_url=return_url
                )
                logger.info(f"Click link generated: {pay_link}")
                return Response({"success": True, "payment_link": pay_link}, status=status.HTTP_200_OK)

            return Response({"success": True, "message": "Buyurtma rasmiylashtirildi", "order_id": order.id}, status=status.HTTP_200_OK)

        else:
            logger.warning(f"Checkout validation error: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


