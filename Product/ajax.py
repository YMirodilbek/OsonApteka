from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .context_processors import cart_context
from Product.models import Dostafca ,Product
from .lotin_krill import latin_to_cyrillic
from django.http import JsonResponse
from django.db.models import Q
from rapidfuzz import fuzz
from .views import *

@login_required(login_url='/auth/send-otp/')
def add_to_cart(request, product_id):
    
    product = get_object_or_404(Product, id=product_id)
    r = redis.Redis(host='localhost', port=6379, db=0)
    result = r.get('final_result') 
    if result:
        result = json.loads(result.decode('utf-8'))
    
    
    result_dict = {item['id']: item for item in result}
    price = result_dict.get( product_id, {}).get('prices', [0])
    name= result_dict.get(product_id, {}).get('name', '')

    
    order = Order.objects.filter(user=request.user, is_completed=False).first()

    if not order:
        order = Order.objects.create(user=request.user, is_completed=False)
    order_item, created = OrderItem.objects.get_or_create(
                                    order = order,      
                                    product = product,
                                    price = price[0],
                                    name = name,
                                    )

    if not created:
        order_item.quantity += 1
        order_item.save()
        
    cart =  cart_context(request)
    cart_count = len(cart['cart_items'])
    cart_total = cart['cart_total']
    # messages.success(request, " mahsulot Savatchaga qo'shildi ")
    return JsonResponse({"status":200,'cart_count':cart_count, 'cart_total':cart_total})


def search_products(request):
    query = latin_to_cyrillic(request.GET.get('q', '')).strip().lower()
    matched_items = []
    if len(query) >= 4:
        r = redis.Redis(host='localhost', port=6379, db=0)
        result = r.get('final_result')

        if result and query:
            result = json.loads(result.decode('utf-8'))
        for  item in result:
            name = item.get('name_lower')

            if name: 
                if query == name or name.startswith(query):
                    matched_items.append(item)
                else:
                    score = fuzz.ratio(query, name)
                    if score >= 35:
                        matched_items.append(item)

    return JsonResponse(matched_items, safe=False)


@csrf_exempt
def update_order_status(request, pk):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            status = data.get('status')
            order = Order.objects.get(pk=pk)
            order.status = status
            order.save()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

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
                    'image1': product.image1.url if product.image1 else None,
                })
       
    return JsonResponse({'results': results})




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







# from .tasks import *
# url = "http://93.170.11.10:8088/RM_OPT/hs/online/stock"
# username = "Online"
# password = "cJXGLytPHb3nDNZf5gRh7jzwa"
# response = requests.post(url, auth=HTTPBasicAuth(username, password), stream=True, json={})
# if response.status_code == 200:
#     data = response.json().get('array', [])
#     uid_list = []

#     for item in data:
#         try:
#             uid = int(item.get("UID"))
#             uid_list.append(uid)
#         except (TypeError, ValueError):
#             continue

#         products = Product.objects.filter(uid__in=uid_list)
#         products_dict = {p.uid: p for p in products}

#         result = []
#         for item in data:
#             try:
#                 uid = int(item.get("UID"))
#             except (TypeError, ValueError):
#                 continue


# grouped_by_class = {}

# for item in data:
#     try:
#         uid = int(item.get("UID"))
#     except (TypeError, ValueError):
#         continue

#     product = products_dict.get(uid)
#     if not product:
#         continue

#     category = item.get("Class", "")
#     product_data = {
#         "id": product.id,
#         "name": item.get("Name", ""),
#         "name_lower": item.get("Name", "").lower(),
#         "price": item.get("Price", 0),
#         "class": category,
#         "producer": item.get("Producer", ""),
#         "country": item.get("Country", ""),
#         "MNN": item.get("MNN", ""),
#         "ReleaseForm": item.get("ReleaseForm", ""),
#         "ProductType": item.get("ProductType", ""),
#         "ExpDate": item.get("ExpDate", ""),
#         "info": product.info,
#         "image1": product.image1.url if product.image1 else "",
#         "image2": product.image2.url if product.image2 else "",
#         "image3": product.image3.url if product.image3 else "",
#     }

#     grouped_by_class.setdefault(category, []).append(product_data)

# # Redisga saqlash (24 soat)
# r.setex('products_by_class', 86400, json.dumps(grouped_by_class))
