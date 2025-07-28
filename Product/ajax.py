from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .context_processors import cart_context
from Product.models import Dostafca ,Product
from .lotin_krill import latin_to_cyrillic
from django.http import JsonResponse
from django.db.models import Q
from rapidfuzz import fuzz
from .views import *
import json
from .decorator import login_required_ajax

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

