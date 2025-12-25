from .lotin_krill import latin_to_cyrillic, compress, compress_2
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .context_processors import cart_context
from Product.models import Dostafca ,Product
from .decorator import login_required_ajax
from django.http import JsonResponse
from django.db.models import Q, Max
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from rapidfuzz import fuzz
# from .views import *
import redis
import json

r = redis.Redis(host='localhost', port=6379, db=0)
@login_required_ajax
def add_to_cart(request, product_id):
    
    product = get_object_or_404(Product, id=product_id)
    if product.product_type == "Рецепт билан":
        return JsonResponse({"status":300})
    data = json.loads(request.body)
    price = int(data.get('price') or 0)

    if price <= 0:
        price_obj = product.product_prise.filter(price__gt=0).order_by('price').first()
        if price_obj:
            price = price_obj.price
        else:
            price = 0  
    
    
    
    order = Order.objects.filter(user=request.user, is_completed=False).first()

    if not order:
        order = Order.objects.create(user=request.user, is_completed=False)
    order_item, created = OrderItem.objects.get_or_create(
                                    order = order,      
                                    product = product,
                                    price = price,
                                    name = product.name,
                                    )

    if not created:
        order_item.quantity += 1
        order_item.save()
        
    cart =  cart_context(request)
    cart_count = len(cart['cart_items'])
    cart_total = cart['cart_total']
    return JsonResponse({"status":200,'cart_count':cart_count, 'cart_total':cart_total})


def search_products(request):
    query = latin_to_cyrillic(request.GET.get('q', ''))

    matched_items = []

    if len(query) >= 3:
        product_prices_qs = ProductPrice.objects.filter(price__gt=0, amount__gt=0)

        result = Product.objects.filter(name__icontains=query).prefetch_related(
            Prefetch('product_prise', queryset=product_prices_qs, to_attr='valid_prices')
        )
        
        for item in result:
            if not item.valid_prices:
                continue

            price_obj = item.valid_prices[0]
            image_url = item.image1.url if item.image1 else None

            matched_items.append({
                "id": item.id,
                "name": item.name,
                "producer": item.producer,
                "image1": image_url,
                "price": price_obj.price,
            })
    return JsonResponse(matched_items, safe=False)


@csrf_exempt
def update_order_status(request, pk):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            status = data.get('status', '').strip()
            order = Order.objects.get(pk=pk)
            original_status = order.status.strip()  # yozishda xato bo‘lmasin
            
            # Normalize qilish (kichik harf va bo‘sh joylarni olib tashlash)
            normalized_status = status.replace(' ', '').lower()
            normalized_original_status = original_status.replace(' ', '').lower()

            order.status = status  # original qiymatni yozamiz
            order.save()
            
            try:
                user = order.user
                balance = VirtualCard.objects.get(user=user)
                bonus_key = f"bonus:{order.id}"

                if normalized_status == 'radetilgan' and normalized_original_status != 'radetilgan' and order.payment_method != "card":
                    bonus_amount = r.get(bonus_key)
                    if bonus_amount:
                        bonus_amount = Decimal(bonus_amount.decode('utf-8'))
                        balance.balance -= bonus_amount
                        balance.save()
                        r.delete(bonus_key)

                elif normalized_original_status == 'radetilgan' and normalized_status != 'radetilgan' and order.payment_method != "card":
                    bonus_amount = Decimal(order.total_price) * Decimal('0.01')
                    balance.balance += bonus_amount
                    balance.save()
                    r.setex(bonus_key, 60 * 60 * 72, str(bonus_amount))

            except:pass
            
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


def product_search_api(request):
    q = request.GET.get('q', '').lower().strip()
    results = []

    if len(q) >= 5:
        products = Product.objects.filter(
                    Q(uid__icontains=q) | Q(name__icontains=latin_to_cyrillic(q))
                )[:20]
        if products.exists():
            for product in products:
                results.append({
                    'id': product.id,
                    'uid': product.uid,
                    'name': product.name,
                    'member':product.member.name  if product.member else None,
                    'image1': product.image1.url if product.image1 else None,
                })
       
    return JsonResponse({'results': results})


@csrf_exempt
def add_product_member(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        member_id = request.POST.get('member_id')

        try:
            product = Product.objects.get(id=product_id)
            if member_id == '0':
                product.member = None
            else:
                product.member_id = member_id
            product.save()
            return JsonResponse({'success': True})
        except Product.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Product topilmadi'})
        

def member_create(request):
    name = request.POST.get("name")
    Member.objects.create(name=name)
    return redirect('member')


def member_delete(request, pk):
    member =  get_object_or_404(Member, id=pk)
    member.delete()
    return redirect('member')



@require_http_methods(["DELETE"])
def delete_product(request, pk):
    from .models import Product
    try:
        product = Product.objects.get(id=pk)
        if product.image1 and os.path.exists(product.image1.path):
            os.remove(product.image1.path)
        product.delete()
        return JsonResponse({'success': True})
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Product not found'}, status=404)


def update_person(request):
    if request.method == "POST":
        person = request.POST.get("person")
        product_id = request.POST.get("product_id")
        try:
            product = Product.objects.get(id=product_id)
            product.category_person = person
            product.save()
            return JsonResponse({"success": True, 'person':product.category_person})
        except Product.DoesNotExist:
            return JsonResponse({"error": "Product not found"}, status=404)
    return JsonResponse({"error": "Invalid method"}, status=400)


def dogovor(request):
    return render(request,'oferta/dogovor.html')


def uslugi(request):
    return render(request,'oferta/uslugi.html')


def document(request):
    return render(request,'oferta/document.html')


def dastafca(request):
    amount = request.POST.get('amount')
    
    dostafca =  Dostafca.objects.last()
    dostafca.amount = int(amount)
    dostafca.save()
    return  redirect('/filial/')


def get_messages(request, user_id):
    five_days_ago = timezone.now() - timedelta(days=5)
    recent_chats = Chat.objects.filter(
        timestamp__gte=five_days_ago,
        user__isnull=False
    )

    users = User.objects.filter(
        chats__in=recent_chats
    ).annotate(
        last_message_time=Max('chats__timestamp')
    ).order_by('-last_message_time').distinct()

    user_data = []
    for user in users:
        user_data.append({
            'id': user.id,
            'first_name': user.first_name if user.first_name else 'N',
            'last_time': user.last_message_time.strftime('%H:%M') if user.last_message_time else '',
            'count': user.cha_count
        })
    
    
    chats = Chat.objects.filter(room_id=user_id).order_by('timestamp')
    chats.filter(is_read_admin=False).update(is_read_admin=True)
    user = CustomUser.objects.get(id=user_id)
    messages = []

    for chat in chats:
        messages.append({
            'admin':chat.user_admin.first_name if chat.user_admin else "",
            'room_id':chat.room_id,
            'content': chat.content,
            'image': chat.image.url if chat.image else None,
            'time': chat.timestamp.strftime('%H:%M'),
            'is_sent_by_me':  chat.room_id == chat.user.id if hasattr(chat, 'user') and chat.user is not None else False
        })

    return JsonResponse({'messages': messages, 'user':user.phone_number, 'users':user_data})

@csrf_exempt
def send_image(request):
    if request.method == 'POST' and request.FILES.get('image'):
        image = request.FILES['image']
        room_id = request.POST.get('room_id')
        chat = Chat.objects.create(
            user_admin=request.user,
            # user_id=room_id,
            room_id=room_id,
            image=image,
            is_read_admin=True,
        )
        return JsonResponse({'success': True, 'image_url': chat.image.url})
    return JsonResponse({'success': False}, status=400)


@csrf_exempt
def send_text(request):
    data = json.loads(request.body)
    content = data.get('content')
    room_id = data.get('room_id')
    if content:
        Chat.objects.create(
            user_admin=request.user,
            # user_id=room_id,
            room_id=room_id,
            content=content,
            is_read_admin=True,
        )
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)



def category_img_edit(request):
    if request.method == "POST":
        cat_id = request.POST.get('id')
        img = request.FILES.get('img')

        if not cat_id or not img:
            return JsonResponse({"success": False, "error": "ID yoki rasm yuborilmadi"})

        try:
            category = Category.objects.get(id=cat_id)
        except Category.DoesNotExist:
            return JsonResponse({"success": False, "error": "Kategoriya topilmadi"})

        category.svg = compress_2(img)
        category.save()

        return JsonResponse({
            "success": True,
            "new_image_url": category.svg.url
        })

    categorys = Category.objects.all()
    return render(request, 'filial/category-edit.html', {'categorys': categorys})