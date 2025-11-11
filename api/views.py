from rest_framework.decorators import api_view,  permission_classes
from rest_framework.permissions import  AllowAny, IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Sum, F, Prefetch, Count, Q
from tmp.models import Landlord, Applicant, GlavniImage
from main.bot_messages import send_telegram_message
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils.timezone import now
from django.http import JsonResponse
from django.shortcuts import render 
from rest_framework import viewsets
from rest_framework import status
from django.conf import settings
from main.views import send_sms
from click_up import ClickUp
from decimal import Decimal
from . serilalizer import *
from main.models import *
import logging
import random
import redis
import re
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
def get_category(request):
    category = Category.objects.filter(svg__isnull=False)
    serializer = CategorySerializer(category, many=True )
    return Response(serializer.data)


@api_view(["GET"])
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
def get_dastafca(request):
    dastafca = Dostafca.objects.last()
    return Response(DastafcaSerializer(dastafca, many=False).data)


@api_view(['GET'])
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



@api_view(['GET'])
def childrens_catalog(request):
    data = [
    {
        "uz": "miya",
        "ru": "ГОЛОВА И НЕРВЫ",
        "data": [
            {
                "uz": "miya",
                "ru": "ГОЛОВА И НЕРВЫ",
                "data": [
                    {
                        "id": 9,
                        "name": "Спокойствие перед сном (дт)"
                    },
                    {
                        "id": 10,
                        "name": "Головная боль (дт)"
                    },
                    {
                        "id": 11,
                        "name": "Тревожность и страхи (дт)"
                    }
                ]
            },
            {
                "uz": "kuz",
                "ru": "ОФТАЛЬМОЛОГИЯ",
                "data": [
                     {
                        "id": 22,
                        "name": "Витамины для зрения (дт)"
                    },
                    {
                        "id": 23,
                        "name": "Конъюктивит (дт)"
                    }
                ]
            },
            {
                "uz": "kulok",
                "ru": "ЗАБОЛЕВАНИЯ УШЕЙ",
                "data": [
                    {
                        "id": 24,
                        "name": "Ушные инфекции (дт)"
                    }
                ]
            },
            {
                "uz": "ogiz",
                "ru": "УХОД ЗА ПОЛОСТЬЮ РТА И НОСА",
                "data": [
                    
                    {
                        "id": 12,
                        "name": "Детское питание (дт)"
                    },
                    {
                        "id": 13,
                        "name": "Стоматит (дт)"
                    },
                    {
                        "id": 14,
                        "name": "Насморк (дт)"
                    },
                       {
                        "id": 15,
                        "name": "Для десен (дт)"
                    }
                ]
            }
        ]
    },
    {
        "uz": "tomog",
        "ru": "ИММУНИТЕТ И БОЛЕЗНИ",
        "data": [
            {
                "uz": "tomog",
                "ru": "ИММУНИТЕТ И БОЛЕЗНИ",
                "data": [
                 
                    {
                        "id": 16,
                        "name": "Простуда и грипп (дт)"
                    },
                    {
                        "id": 17,
                        "name": "Повышение иммунитета (дт)"
                    },
                    {
                        "id": 18,
                        "name": "Аллергии (дт)"
                    },
                    {
                        "id": 19,
                        "name": "Ангина (дт)"
                    }
                ]
            }
        ]
    },
    {
        "uz": "tomog pasti",
        "ru": "ОБЩЕЕ РАЗВИТИЕ",
        "data": [
            {
                "uz": "tomog pasti",
                "ru": "ОБЩЕЕ РАЗВИТИЕ",
                "data": [
                    
                { "id": 20,
                        "name": "Витамины для роста (дт)"
                    },
                    {
                        "id": 21,
                        "name": "Витамины для мозга и памяти (дт)"
                    }
                  
                ]
            }
        ]
    },
    {
        "uz": "oshkozON",
        "ru": "ПИЩЕВАРЕНИЕ",
        "data": [
            {
                "uz": "oshkozON",
                "ru": "ПИЩЕВАРЕНИЕ",
                "data": [
                    {
                        "id": 25,
                        "name": "Болит животик (дт)"
                    },
                    {
                        "id": 26,
                        "name": "Запор / понос (дт)"
                    },
                    {
                        "id": 27,
                        "name": "Плохой аппетит (дт)"
                    }
                ]
            }
        ]
    },
    {
        "uz": "oshkozON pasti",
        "ru": "ПРОЧЕЕ",
        "data": [
            {
                "uz": "oshkozON pasti",
                "ru": "ПРОЧЕЕ",
                "data": [
                    {
                        "id": 28,
                        "name": "Подгузники (дт)"
                    },
                    {
                        "id": 29,
                        "name": "Детская косметика (дт)"
                    }
                ]
            }
        ]
    }
    ]
    return JsonResponse(data, safe=False)


@api_view(['GET'])
def women_catalog(request):
    data = [
    {
        "uz": "miya",
        "ru": "НЕВРОЛОГИЯ",
        "data": [
            {
                "uz": "miya",
                "ru": "НЕВРОЛОГИЯ",
                "data": [
                    {
                        "id": 30,
                        "name": "Бессонница"
                    },
                    {
                        "id": 31,
                        "name": "Витамины группы Б"
                    },
                    {
                        "id": 32,
                        "name": "Витамины для памяти"
                    },
                    {
                        "id": 33,
                        "name": "Головная боль"
                    },
                    {
                        "id": 34,
                        "name": "Мигрень"
                    },
                    {
                        "id": 35,
                        "name": "Зубная боль"
                    },
                    {
                        "id": 36,
                        "name": "Невроз"
                    },
                    {
                        "id": 37,
                        "name": "Стресс"
                    },
                    {
                        "id": 38,
                        "name": "Улучшение памяти"
                    }
                ]
            },
            {
                "uz": "kulok",
                "ru": "ЗАБОЛЕВАНИЯ УШЕЙ",
                "data": [
                    {
                        "id": 46,
                        "name": "Ушные капли"
                    }
                ]
            },
            {
                "uz": "kuz",
                "ru": "ОФТАЛЬМОЛОГИЯ",
                "data": [
                    {
                        "id": 78,
                        "name": "Витамины для глаз"
                    },
                    {
                        "id": 79,
                        "name": "Антисептические капли"
                    },
                    {
                        "id": 80,
                        "name": "Глазные гели"
                    },
                    {
                        "id": 81,
                        "name": "Глаукома"
                    },
                    {
                        "id": 82,
                        "name": "Капли при аллергии"
                    },
                    {
                        "id": 83,
                        "name": "Капли с таурином"
                    },
                    {
                        "id": 84,
                        "name": "Конъюктивит"
                    },
                    {
                        "id": 85,
                        "name": "Покраснение глаз"
                    },
                    {
                        "id": 86,
                        "name": "Увлажняющие капли"
                    }
                ]
            },
            {
                "uz": "burun",
                "ru": "УХОД ЗА ПОЛОСТЬЮ НОСА",
                "data": [
                    {
                        "id": 87,
                        "name": "Аллергический ринит"
                    },
                    {
                        "id": 88,
                        "name": "Аспираторы"
                    },
                    {
                        "id": 89,
                        "name": "Гайморит"
                    },
                    {
                        "id": 90,
                        "name": "Насморк"
                    }
                ]
            },
            {
                "uz": "ogiz",
                "ru": "ГИГИЕНА ПОЛОСТИ РТА И УХОД ЗА ГУБАМИ",
                "data": [
                    {
                        "id": 91,
                        "name": "Воспаление дёсен"
                    },
                    {
                        "id": 92,
                        "name": "Запах изо рта"
                    },
                    {
                        "id": 93,
                        "name": "Зубные нити"
                    },
                    {
                        "id": 94,
                        "name": "Кровоточивость дёсен"
                    },
                    {
                        "id": 95,
                        "name": "Ополаскиватели"
                    },
                    {
                        "id": 96,
                        "name": "Стоматит"
                    }
                ]
            },
            {
                "uz": "soch",
                "ru": "УХОД ЗА ВОЛОСАМИ",
                "data": [
                    {
                        "id": 39,
                        "name": "Бальзамы для волос"
                    },
                    {
                        "id": 40,
                        "name": "Витамины для волос"
                    },
                    {
                        "id": 41,
                        "name": "Для восстановления волос"
                    },
                    {
                        "id": 42,
                        "name": "Кондиционеры для волос"
                    },
                    {
                        "id": 43,
                        "name": "Перхоть"
                    },
                    {
                        "id": 44,
                        "name": "Против выпадения"
                    },
                    {
                        "id": 45,
                        "name": "Укрепление волос"
                    }
                ]
            },
            {
                "uz": "yuz",
                "ru": "СРЕДСТВА ДЛЯ УХОДА ЗА КОЖЕЙ ЛИЦА",
                "data": [
                    {
                        "id": 47,
                        "name": "Маски для лица"
                    },
                    {
                        "id": 48,
                        "name": "Кремы для лица"
                    },
                    {
                        "id": 49,
                        "name": "Сыворотки для лица"
                    },
                    {
                        "id": 50,
                        "name": "Угревая сыпь"
                    }
                ]
            }
        ]
    },
    {
       "uz": "tomog",
        "ru": "ПРОСТУДНЫЕ ЗАБОЛЕВАНИЯ И ИММУНИТЕТ",
        "data": [
            {
                "uz": "tomog",
                "ru": "ПРОСТУДНЫЕ ЗАБОЛЕВАНИЯ И ИММУНИТЕТ",
                "data": [
                    {
                        "id": 51,
                        "name": "Ангина"
                    },
                    {
                        "id": 52,
                        "name": "Боль в горле"
                    },
                    {
                        "id": 53,
                        "name": "От простуды"
                    }
                ]
            }
        ]
    },
    {
        "uz": "upka",
        "ru": "ЛЕЧЕНИЕ ДЫХАТЕЛЬНОЙ СИСТЕМЫ",
        "data": [
            {
                "uz": "upka",
                "ru": "ЛЕЧЕНИЕ ДЫХАТЕЛЬНОЙ СИСТЕМЫ",
                "data": [
                    {
                        "id": 54,
                        "name": "Бронхиальная астма"
                    },
                    {
                        "id": 55,
                        "name": "Влажный кашель"
                    },
                    {
                        "id": 56,
                        "name": "Сухой кашель"
                    },
                    {
                        "id": 57,
                        "name": "Небулайзеры"
                    }
                ]
            },
            {
                "uz": "yurak teparogi",
                "ru": "ОСАНКА",
                "data": [
                    {
                        "id": 116,
                        "name": "Бандажи женские"
                    },
                    {
                        "id": 117,
                        "name": "Корректоры осанки"
                    },
                    {
                        "id": 118,
                        "name": "Корсеты"
                    },
                    {
                        "id": 119,
                        "name": "Люмбосакральные бандажи"
                    }
                ]
            },
            {
                "uz": "yurak",
                "ru": "СЕРДЕЧНО-СОСУДИСТАЯ СИСТЕМА",
                "data": [
                    {
                        "id": 97,
                        "name": "Ангиопротекторы"
                    },
                    {
                        "id": 98,
                        "name": "Антиагреганты"
                    },
                    {
                        "id": 99,
                        "name": "Аритмия"
                    },
                    {
                        "id": 100,
                        "name": "Высокое давление"
                    },
                    {
                        "id": 101,
                        "name": "Для сердца и сосудов"
                    },
                    {
                        "id": 102,
                        "name": "Низкое давление"
                    },
                    {
                        "id": 103,
                        "name": "Стенокардия"
                    },
                    {
                        "id": 104,
                        "name": "Тонометры"
                    },
                    {
                        "id": 105,
                        "name": "Холестерин"
                    }
                ]
            }
        ]
    },
    {
        "uz": "kul tomiri",
        "ru": "ЗАБОЛЕВАНИЯ КРОВИ",
        "data": [
            {
                "uz": "kul tomiri",
                "ru": "ЗАБОЛЕВАНИЯ КРОВИ",
                "data": [
                    {
                        "id": 136,
                        "name": "Антикоагулянты"
                    },
                    {
                        "id": 137,
                        "name": "Кровоостанавливающие"
                    }
                ]
            },
            {
                "uz": "kul/tirnoq",
                "ru": "УХОД ЗА РУКАМИ",
                "data": [
                    {
                        "id": 138,
                        "name": "Витамины для ногтей"
                    },
                    {
                        "id": 139,
                        "name": "Жидкости для снятия лака"
                    },
                    {
                        "id": 140,
                        "name": "Кремы для рук"
                    },
                    {
                        "id": 141,
                        "name": "Масла для ногтей"
                    },
                    {
                        "id": 142,
                        "name": "Пилки"
                    },
                    {
                        "id": 143,
                        "name": "Укрепители ногтей"
                    },
                    {
                        "id": 144,
                        "name": "Умная эмаль"
                    }
                ]
            }
        ]
    },
    {
        "uz": "ichaklar",
        "ru": "ЗАБОЛЕВАНИЯ КИШЕЧНИКА",
        "data": [
            {
                "uz": "ichaklar",
                "ru": "ЗАБОЛЕВАНИЯ КИШЕЧНИКА",
                "data": [
                    {
                        "id": 106,
                        "name": "Диарея"
                    },
                    {
                        "id": 107,
                        "name": "Запор"
                    },
                    {
                        "id": 108,
                        "name": "Изжога"
                    },
                    {
                        "id": 109,
                        "name": "Метеоризм"
                    },
                    {
                        "id": 110,
                        "name": "Пробиотики"
                    },
                    {
                        "id": 111,
                        "name": "Сорбенты"
                    },
                    {
                        "id": 112,
                        "name": "Спазмы"
                    },
                    {
                        "id": 113,
                        "name": "Тошнота"
                    },
                    {
                        "id": 114,
                        "name": "Тяжесть в желудке"
                    },
                    {
                        "id": 115,
                        "name": "Язва и гастрит"
                    }
                ]
            },
            {
                "uz": "jigar",
                "ru": "ЗАБОЛЕВАНИЯ ПЕЧЕНИ",
                "data": [
                    {
                        "id": 58,
                        "name": "Гепатит"
                    },
                    {
                        "id": 59,
                        "name": "Желчегонные сборы"
                    },
                    {
                        "id": 60,
                        "name": "Жировая болезнь печени"
                    },
                    {
                        "id": 61,
                        "name": "Камни в желчном пузыре"
                    },
                    {
                        "id": 62,
                        "name": "Расторопша"
                    },
                    {
                        "id": 63,
                        "name": "Холецистит"
                    },
                    {
                        "id": 64,
                        "name": "Цирроз"
                    }
                ]
            },
            {
                "uz": "ichaklar teparogi/bel",
                "ru": "МЕДИЦИНСКИЕ ПОЯСА",
                "data": [
                    {
                        "id": 120,
                        "name": "Пояс согревающий"
                    },
                    {
                        "id": 121,
                        "name": "Пояс дородовой"
                    },
                    {
                        "id": 122,
                        "name": "Пояс послеродовой"
                    }
                ]
            }
        ]
    },
    {
        "uz": "ichaklar pastrigi/gemmoroy",
        "ru": "АНТИГЕМОРРОИДАЛЬНЫЕ СРЕДСТВА",
        "data": [
            {
                "uz": "ichaklar pastrigi/gemmoroy",
                "ru": "АНТИГЕМОРРОИДАЛЬНЫЕ СРЕДСТВА",
                "data": [
                    {
                        "id": 123,
                        "name": "Мази от геморроя"
                    },
                    {
                        "id": 124,
                        "name": "Свечи от геморроя"
                    },
                    {
                        "id": 125,
                        "name": "Таблетки от геморроя"
                    }
                ]
            },
            {
                "uz": "buyrak",
                "ru": "ПОЧКИ И МОЧЕВЫДЕЛИТЕЛЬНАЯ СИСТЕМА",
                "data": [
                    {
                        "id": 65,
                        "name": "Мочегонные средства"
                    },
                    {
                        "id": 66,
                        "name": "Пиелонефрит"
                    },
                    {
                        "id": 67,
                        "name": "Урологические сборы"
                    },
                    {
                        "id": 68,
                        "name": "Цистит"
                    }
                ]
            },
            {
                "uz": "reproduktiv/jinsiy tizim",
                "ru": "РЕПРОДУКТИВНАЯ СИСТЕМА",
                "data": [
                    {
                        "id": 69,
                        "name": "Бесплодие"
                    },
                    {
                        "id": 70,
                        "name": "Климакс"
                    },
                    {
                        "id": 71,
                        "name": "Кольпит"
                    },
                    {
                        "id": 72,
                        "name": "Молочница"
                    },
                    {
                        "id": 73,
                        "name": "Противозачаточные"
                    },
                    {
                        "id": 74,
                        "name": "Струйные тесты"
                    },
                    {
                        "id": 75,
                        "name": "Тесты"
                    },
                    {
                        "id": 76,
                        "name": "Трихомониаз"
                    },
                    {
                        "id": 77,
                        "name": "Эндометриоз"
                    }
     
                ]
            }
        ]
    },
    {
        "uz": "tizza",
        "ru": "ЗАБОЛЕВАНИЯ КОСТЕЙ И СУСТАВОВ",
        "data": [
            {
                "uz": "tizza",
                "ru": "ЗАБОЛЕВАНИЯ КОСТЕЙ И СУСТАВОВ",
                "data": [
                    {
                        "id": 145,
                        "name": "Артрит"
                    },
                    {
                        "id": 146,
                        "name": "Артроз"
                    },
                    {
                        "id": 147,
                        "name": "Боль в суставах"
                    },
                    {
                        "id": 148,
                        "name": "Обезбаливающие мази"
                    },
                    {
                        "id": 149,
                        "name": "Ушибы"
                    },
                    {
                        "id": 150,
                        "name": "Хондроитин и глюкозамин"
                    }
                ]
            },
            {
                "uz": "buzoklar/oyoq tomirlari",
                "ru": "ЗАБОЛЕВАНИЯ ВЕН",
                "data": [
                    {
                        "id": 126,
                        "name": "Бинты"
                    },
                    {
                        "id": 127,
                        "name": "Варикоз"
                    },
                    {
                        "id": 128,
                        "name": "Гольфы"
                    },
                    {
                        "id": 129,
                        "name": "Колготки"
                    },
                    {
                        "id": 130,
                        "name": "Чулки"
                    },
                    {
                        "id": 131,
                        "name": "Отеки"
                    }
                ]
            },
            {
                "uz": "ikkinchi oyoq tugmachasi",
                "ru": "ПЛАСТЫРИ",
                "data": [
                    {
                        "id": 132,
                        "name": "В рулоне"
                    },
                    {
                        "id": 133,
                        "name": "От сухих мозолей"
                    },
                    {
                        "id": 134,
                        "name": "От влажных мозолей"
                    },
                    {
                        "id": 135,
                        "name": "Салипод"
                    }
                ]
            },
            {
                "uz": "oyoq eng pastdagi tugmachasi",
                "ru": "УХОД И СРЕДСТВА ДЛЯ НОГ",
                "data": [
                    {
                        "id": 151,
                        "name": "Гели для ног"
                    },
                    {
                        "id": 152,
                        "name": "Кремы для ног"
                    },
                    {
                        "id": 153,
                        "name": "От запаха"
                    },
                    {
                        "id": 154,
                        "name": "От мозолей"
                    },
                    {
                        "id": 155,
                        "name": "От натоптышей"
                    },
                    {
                        "id": 156,
                        "name": "От пота для ног"
                    },
                    {
                        "id": 157,
                        "name": "От трещин на пятках"
                    },
                    {
                        "id": 158,
                        "name": "Терки для ног"
                    }
                ]
            }
        ]
    }
    ]
    return JsonResponse(data, safe=False)


@api_view(['GET'])
def male_catalog(request):
    data = [
    {
        "uz": "miya",
        "ru": "НЕВРОЛОГИЯ",
        "data": [
            {
                "uz": "miya",
                "ru": "НЕВРОЛОГИЯ",
                "data": [
                    {
                        "id": 30,
                        "name": "Бессонница"
                    },
                    {
                        "id": 31,
                        "name": "Витамины группы Б"
                    },
                    {
                        "id": 32,
                        "name": "Витамины для памяти"
                    },
                    {
                        "id": 33,
                        "name": "Головная боль"
                    },
                    {
                        "id": 34,
                        "name": "Мигрень"
                    },
                    {
                        "id": 35,
                        "name": "Зубная боль"
                    },
                    {
                        "id": 36,
                        "name": "Невроз"
                    },
                    {
                        "id": 37,
                        "name": "Стресс"
                    },
                    {
                        "id": 38,
                        "name": "Улучшение памяти"
                    }
                ]
            },
            {
                "uz": "kulok",
                "ru": "ЗАБОЛЕВАНИЯ УШЕЙ",
                "data": [
                    {
                        "id": 46,
                        "name": "Ушные капли"
                    }
                ]
            },
            {
                "uz": "kuz",
                "ru": "ОФТАЛЬМОЛОГИЯ",
                "data": [
                    {
                        "id": 78,
                        "name": "Витамины для глаз"
                    },
                    {
                        "id": 79,
                        "name": "Антисептические капли"
                    },
                    {
                        "id": 80,
                        "name": "Глазные гели"
                    },
                    {
                        "id": 81,
                        "name": "Глаукома"
                    },
                    {
                        "id": 82,
                        "name": "Капли при аллергии"
                    },
                    {
                        "id": 83,
                        "name": "Капли с таурином"
                    },
                    {
                        "id": 84,
                        "name": "Конъюктивит"
                    },
                    {
                        "id": 85,
                        "name": "Покраснение глаз"
                    },
                    {
                        "id": 86,
                        "name": "Увлажняющие капли"
                    }
                ]
            },
            {
                "uz": "burun",
                "ru": "УХОД ЗА ПОЛОСТЬЮ НОСА",
                "data": [
                    {
                        "id": 87,
                        "name": "Аллергический ринит"
                    },
                    {
                        "id": 88,
                        "name": "Аспираторы"
                    },
                    {
                        "id": 89,
                        "name": "Гайморит"
                    },
                    {
                        "id": 90,
                        "name": "Насморк"
                    }
                ]
            },
            {
                "uz": "ogiz",
                "ru": "ГИГИЕНА ПОЛОСТИ РТА И УХОД ЗА ГУБАМИ",
                "data": [
                    {
                        "id": 91,
                        "name": "Воспаление дёсен"
                    },
                    {
                        "id": 92,
                        "name": "Запах изо рта"
                    },
                    {
                        "id": 93,
                        "name": "Зубные нити"
                    },
                    {
                        "id": 94,
                        "name": "Кровоточивость дёсен"
                    },
                    {
                        "id": 95,
                        "name": "Ополаскиватели"
                    },
                    {
                        "id": 96,
                        "name": "Стоматит"
                    }
                ]
            },
            {
                "uz": "soch",
                "ru": "УХОД ЗА ВОЛОСАМИ",
                "data": [
                    {
                        "id": 39,
                        "name": "Бальзамы для волос"
                    },
                    {
                        "id": 40,
                        "name": "Витамины для волос"
                    },
                    {
                        "id": 41,
                        "name": "Для восстановления волос"
                    },
                    {
                        "id": 42,
                        "name": "Кондиционеры для волос"
                    },
                    {
                        "id": 43,
                        "name": "Перхоть"
                    },
                    {
                        "id": 44,
                        "name": "Против выпадения"
                    },
                    {
                        "id": 45,
                        "name": "Укрепление волос"
                    }
                ]
            },
            {
                "uz": "yuz",
                "ru": "СРЕДСТВА ДЛЯ УХОДА ЗА КОЖЕЙ ЛИЦА",
                "data": [
                    {
                        "id": 47,
                        "name": "Маски для лица"
                    },
                    {
                        "id": 48,
                        "name": "Кремы для лица"
                    },
                    {
                        "id": 49,
                        "name": "Сыворотки для лица"
                    },
                    {
                        "id": 50,
                        "name": "Угревая сыпь"
                    }
                ]
            }
        ]
    },
    {
       "uz": "tomog",
        "ru": "ПРОСТУДНЫЕ ЗАБОЛЕВАНИЯ И ИММУНИТЕТ",
        "data": [
            {
                "uz": "tomog",
                "ru": "ПРОСТУДНЫЕ ЗАБОЛЕВАНИЯ И ИММУНИТЕТ",
                "data": [
                    {
                        "id": 51,
                        "name": "Ангина"
                    },
                    {
                        "id": 52,
                        "name": "Боль в горле"
                    },
                    {
                        "id": 53,
                        "name": "От простуды"
                    }
                ]
            }
        ]
    },
    {
        "uz": "upka",
        "ru": "ЛЕЧЕНИЕ ДЫХАТЕЛЬНОЙ СИСТЕМЫ",
        "data": [
            {
                "uz": "upka",
                "ru": "ЛЕЧЕНИЕ ДЫХАТЕЛЬНОЙ СИСТЕМЫ",
                "data": [
                    {
                        "id": 54,
                        "name": "Бронхиальная астма"
                    },
                    {
                        "id": 55,
                        "name": "Влажный кашель"
                    },
                    {
                        "id": 56,
                        "name": "Сухой кашель"
                    },
                    {
                        "id": 57,
                        "name": "Небулайзеры"
                    }
                ]
            },
            {
                "uz": "yurak teparogi",
                "ru": "ОСАНКА",
                "data": [
                    {
                        "id": 116,
                        "name": "Бандажи женские"
                    },
                    {
                        "id": 117,
                        "name": "Корректоры осанки"
                    },
                    {
                        "id": 118,
                        "name": "Корсеты"
                    },
                    {
                        "id": 119,
                        "name": "Люмбосакральные бандажи"
                    }
                ]
            },
            {
                "uz": "yurak",
                "ru": "СЕРДЕЧНО-СОСУДИСТАЯ СИСТЕМА",
                "data": [
                    {
                        "id": 97,
                        "name": "Ангиопротекторы"
                    },
                    {
                        "id": 98,
                        "name": "Антиагреганты"
                    },
                    {
                        "id": 99,
                        "name": "Аритмия"
                    },
                    {
                        "id": 100,
                        "name": "Высокое давление"
                    },
                    {
                        "id": 101,
                        "name": "Для сердца и сосудов"
                    },
                    {
                        "id": 102,
                        "name": "Низкое давление"
                    },
                    {
                        "id": 103,
                        "name": "Стенокардия"
                    },
                    {
                        "id": 104,
                        "name": "Тонометры"
                    },
                    {
                        "id": 105,
                        "name": "Холестерин"
                    }
                ]
            }
        ]
    },
    {
        "uz": "kul tomiri",
        "ru": "ЗАБОЛЕВАНИЯ КРОВИ",
        "data": [
            {
                "uz": "kul tomiri",
                "ru": "ЗАБОЛЕВАНИЯ КРОВИ",
                "data": [
                    {
                        "id": 136,
                        "name": "Антикоагулянты"
                    },
                    {
                        "id": 137,
                        "name": "Кровоостанавливающие"
                    }
                ]
            },
            {
                "uz": "kul/tirnoq",
                "ru": "УХОД ЗА РУКАМИ",
                "data": [
                    {
                        "id": 138,
                        "name": "Витамины для ногтей"
                    },
                    {
                        "id": 139,
                        "name": "Жидкости для снятия лака"
                    },
                    {
                        "id": 140,
                        "name": "Кремы для рук"
                    },
                    {
                        "id": 141,
                        "name": "Масла для ногтей"
                    },
                    {
                        "id": 142,
                        "name": "Пилки"
                    },
                    {
                        "id": 143,
                        "name": "Укрепители ногтей"
                    },
                    {
                        "id": 144,
                        "name": "Умная эмаль"
                    }
                ]
            }
        ]
    },
    {
        "uz": "ichaklar",
        "ru": "ЗАБОЛЕВАНИЯ КИШЕЧНИКА",
        "data": [
            {
                "uz": "ichaklar",
                "ru": "ЗАБОЛЕВАНИЯ КИШЕЧНИКА",
                "data": [
                    {
                        "id": 106,
                        "name": "Диарея"
                    },
                    {
                        "id": 107,
                        "name": "Запор"
                    },
                    {
                        "id": 108,
                        "name": "Изжога"
                    },
                    {
                        "id": 109,
                        "name": "Метеоризм"
                    },
                    {
                        "id": 110,
                        "name": "Пробиотики"
                    },
                    {
                        "id": 111,
                        "name": "Сорбенты"
                    },
                    {
                        "id": 112,
                        "name": "Спазмы"
                    },
                    {
                        "id": 113,
                        "name": "Тошнота"
                    },
                    {
                        "id": 114,
                        "name": "Тяжесть в желудке"
                    },
                    {
                        "id": 115,
                        "name": "Язва и гастрит"
                    }
                ]
            },
            {
                "uz": "jigar",
                "ru": "ЗАБОЛЕВАНИЯ ПЕЧЕНИ",
                "data": [
                    {
                        "id": 58,
                        "name": "Гепатит"
                    },
                    {
                        "id": 59,
                        "name": "Желчегонные сборы"
                    },
                    {
                        "id": 60,
                        "name": "Жировая болезнь печени"
                    },
                    {
                        "id": 61,
                        "name": "Камни в желчном пузыре"
                    },
                    {
                        "id": 62,
                        "name": "Расторопша"
                    },
                    {
                        "id": 63,
                        "name": "Холецистит"
                    },
                    {
                        "id": 64,
                        "name": "Цирроз"
                    }
                ]
            },
            {
                "uz": "ichaklar teparogi/bel",
                "ru": "МЕДИЦИНСКИЕ ПОЯСА",
                "data": [
                    {
                        "id": 120,
                        "name": "Пояс согревающий"
                    },
                    {
                        "id": 121,
                        "name": "Пояс дородовой"
                    },
                    {
                        "id": 122,
                        "name": "Пояс послеродовой"
                    }
                ]
            }
        ]
    },
    {
        "uz": "ichaklar pastrigi/gemmoroy",
        "ru": "АНТИГЕМОРРОИДАЛЬНЫЕ СРЕДСТВА",
        "data": [
            {
                "uz": "ichaklar pastrigi/gemmoroy",
                "ru": "АНТИГЕМОРРОИДАЛЬНЫЕ СРЕДСТВА",
                "data": [
                    {
                        "id": 123,
                        "name": "Мази от геморроя"
                    },
                    {
                        "id": 124,
                        "name": "Свечи от геморроя"
                    },
                    {
                        "id": 125,
                        "name": "Таблетки от геморроя"
                    }
                ]
            },
            {
                "uz": "buyrak",
                "ru": "ПОЧКИ И МОЧЕВЫДЕЛИТЕЛЬНАЯ СИСТЕМА",
                "data": [
                    {
                        "id": 65,
                        "name": "Мочегонные средства"
                    },
                    {
                        "id": 66,
                        "name": "Пиелонефрит"
                    },
                    {
                        "id": 67,
                        "name": "Урологические сборы"
                    },
                    {
                        "id": 68,
                        "name": "Цистит"
                    }
                ]
            },
            {
                "uz": "reproduktiv/jinsiy tizim",
                "ru": "РЕПРОДУКТИВНАЯ СИСТЕМА",
                "data": [
                    {
                        "id": 69,
                        "name": "Бесплодие"
                    },
                      {
                    "id": 159,
                    "name": "Для потенции"
                },
                {
                    "id": 160,
                    "name": "Презервативы"
                },
                {
                    "id": 161,
                    "name": "Простатит"
                }
                ]
            }
        ]
    },
    {
        "uz": "tizza",
        "ru": "ЗАБОЛЕВАНИЯ КОСТЕЙ И СУСТАВОВ",
        "data": [
            {
                "uz": "tizza",
                "ru": "ЗАБОЛЕВАНИЯ КОСТЕЙ И СУСТАВОВ",
                "data": [
                    {
                        "id": 145,
                        "name": "Артрит"
                    },
                    {
                        "id": 146,
                        "name": "Артроз"
                    },
                    {
                        "id": 147,
                        "name": "Боль в суставах"
                    },
                    {
                        "id": 148,
                        "name": "Обезбаливающие мази"
                    },
                    {
                        "id": 149,
                        "name": "Ушибы"
                    },
                    {
                        "id": 150,
                        "name": "Хондроитин и глюкозамин"
                    }
                ]
            },
            {
                "uz": "buzoklar/oyoq tomirlari",
                "ru": "ЗАБОЛЕВАНИЯ ВЕН",
                "data": [
                    {
                        "id": 126,
                        "name": "Бинты"
                    },
                    {
                        "id": 127,
                        "name": "Варикоз"
                    },
                    {
                        "id": 128,
                        "name": "Гольфы"
                    },
                    {
                        "id": 129,
                        "name": "Колготки"
                    },
                    {
                        "id": 130,
                        "name": "Чулки"
                    },
                    {
                        "id": 131,
                        "name": "Отеки"
                    }
                ]
            },
            {
                "uz": "ikkinchi oyoq tugmachasi",
                "ru": "ПЛАСТЫРИ",
                "data": [
                    {
                        "id": 132,
                        "name": "В рулоне"
                    },
                    {
                        "id": 133,
                        "name": "От сухих мозолей"
                    },
                    {
                        "id": 134,
                        "name": "От влажных мозолей"
                    },
                    {
                        "id": 135,
                        "name": "Салипод"
                    }
                ]
            },
            {
                "uz": "oyoq eng pastdagi tugmachasi",
                "ru": "УХОД И СРЕДСТВА ДЛЯ НОГ",
                "data": [
                    {
                        "id": 151,
                        "name": "Гели для ног"
                    },
                    {
                        "id": 152,
                        "name": "Кремы для ног"
                    },
                    {
                        "id": 153,
                        "name": "От запаха"
                    },
                    {
                        "id": 154,
                        "name": "От мозолей"
                    },
                    {
                        "id": 155,
                        "name": "От натоптышей"
                    },
                    {
                        "id": 156,
                        "name": "От пота для ног"
                    },
                    {
                        "id": 157,
                        "name": "От трещин на пятках"
                    },
                    {
                        "id": 158,
                        "name": "Терки для ног"
                    }
                ]
            }
        ]
    }
    ]


    return JsonResponse(data, safe=False)


@api_view(['GET'])
def glavni (request):
    glavni = GlavniImage.objects.all().order_by('id')
    return Response(GlavniImageSerializer(glavni, many=True).data)

@api_view(['GET'])
def google_api(request):
    data = {
        "success": True,
    }
    return JsonResponse(data)