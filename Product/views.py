from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.contrib import messages
from django.shortcuts import render
from .lotin_krill import compress
from unidecode import unidecode
from .models import *
from .forms import  *
import redis
import json


@login_required(login_url='/auth/send-otp/')
def cart_view(request):
    order = Order.objects.filter(user=request.user, is_completed=False).first()  
    return render(request, "cart.html", {"order": order})
    
def Index(request):

    r = redis.Redis(host='localhost', port=6379, db=0)
    category = request.GET.get('category')
    page = int(request.GET.get("page", 1))
    per_page_classes = 77
    per_class_limit = 100

    # Redisdan olib kelish
    grouped_data_json = r.get('products_by_class')

    grouped_by_class = json.loads(grouped_data_json)

    # 🔴 Faqat bo'sh bo'lmagan classlarni olamiz
    filtered_classes = [
        # class_name for class_name, items in grouped_by_class.items() if items
        class_name for class_name, items in grouped_by_class.items()
       if len(items) >= 2
    ]
    paginator = Paginator(filtered_classes, per_page_classes)



    selected_classes = paginator.page(page).object_list

    result = []
    
    for class_name in selected_classes:
        items = grouped_by_class[class_name][:per_class_limit]
        result.append({
        "class_name": class_name,
        "products": items
        })
    
    if category:
        result = r.get('products_by_class') 
        if result:
            result = json.loads(result.decode('utf-8'))
            result = [{category:result.get(category, [])}]
    

    # if category:
    #     result = r.get('products_by_class')
    #     if result:
    #         result = json.loads(result.decode('utf-8'))
    #         result = result.get(category, [])
    #         # if len(result) >= 10:
    #         result = [{category: result}]
        
    context = {
        "data":result,
        "current_page": page,
        "total_pages": paginator.num_pages,
    }
    return render(request,'index.html', context)


        
        
        
        
    
        


    context = {
        "data":result
    }
    return render(request,'index.html', context)



@login_required(login_url='/auth/send-otp/')
def increase_quantity(request, item_id):
    """Mahsulot miqdorini oshirish"""
    order_item = get_object_or_404(OrderItem, id=item_id, order__user=request.user, order__is_completed=False)
    order_item.quantity += 1
    order_item.save()
    return redirect("cart")


@login_required(login_url='/auth/send-otp/')
def decrease_quantity(request, item_id):
    """Mahsulot miqdorini kamaytirish (0 ga yetganda o‘chirish)"""
    order_item = get_object_or_404(OrderItem, id=item_id, order__user=request.user, order__is_completed=False)

    if order_item.quantity > 1:
        order_item.quantity -= 1
        order_item.save()
    else:
        order_item.delete()  
    return redirect("cart")

@login_required(login_url='/auth/send-otp/')
def DeleteProduct(request, item_id):
    """ Savatdan bitta mahsulot turini butunlay o‘chirish """
    # order = Order.objects.filter(user=request.user, is_completed=False)
    order_item = OrderItem.objects.get( id=item_id)
    if order_item:
        order_item.delete()
    return redirect("cart")  



def product_detail(request,pk):
    product = Product.objects.get(id=int(pk))
    r = redis.Redis(host='localhost', port=6379, db=0)
    result = r.get('final_result') 
    if result:
        result = json.loads(result.decode('utf-8'))

    result_dict = {item['id']: item for item in result}
    product = result_dict.get(product.id, {})

    context = {
        "product":product
    }
    return render(request, 'product-details.html',  context )

@login_required(login_url='/auth/send-otp/')
def add_to_cart_detail(request,pk):
    quantity = int(request.GET.get('quantity',1))
    product = get_object_or_404(Product, id=pk)
    r = redis.Redis(host='localhost', port=6379, db=0)
    result = r.get('final_result') 
    if result:
        result = json.loads(result.decode('utf-8'))
    
    
    result_dict = {item['id']: item for item in result}
    price = result_dict.get(pk, {}).get('price', 0)
    name = result_dict.get(pk, {}).get('name', '')

    print(name)
    print(name)
    print(name)
    print(name)
    order, created = Order.objects.get_or_create(user=request.user, is_completed=False)
    order_item, created = OrderItem.objects.get_or_create(
                                    order=order,      
                                    product=product,
                                    price =price,
                                    name = name,
                                    defaults={quantity:quantity}
                                    )

    if not created:
        order_item.quantity += quantity
        order_item.save()
    return redirect(f'/product/detail/{pk}')

def checkout_view(request):
    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
           
            full_name = form.cleaned_data['full_name']
            phone_number = form.cleaned_data['phone_number']
            payment_method = form.cleaned_data['payment_method']
            address = form.cleaned_data['address']

            

            return redirect('order_success')  
    else:
        form = CheckoutForm()

    return render(request, 'checkout.html', {'form': form})


def Myaccount(request):
    return render(request,'my-account.html')



@login_required
def toggle_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist_item = Wishlist.objects.filter(user=request.user, product=product)

    if wishlist_item.exists():
        wishlist_item.delete()
        messages.success(request, "Mahsulot wishlistdan olib tashlandi!")
    else:
        Wishlist.objects.create(user=request.user, product=product)
        messages.success(request, "Mahsulot wishlistga qo‘shildi!")

    return redirect(request.META.get('HTTP_REFERER', 'wishlist')) 


@login_required(login_url='/auth/send-otp/')
def wishlist_view(request):
    wishlist_items= Wishlist.objects.filter(user=request.user)
    context = {
        'wishlist_items': wishlist_items,
    }
    return render(request,'wishlist.html',context)


def Contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/contact/')
        else:
            messages.error('Iltimos Hamma Maydonlar Toldirilganligiga Etibor bering! ')
    else:
        form = ContactForm()

    context={
        'form':form
    }

    return render(request,'contact.html',context)


def checkout_view(request):
    cart_items = request.user.cart.items.all()  

    if not cart_items:
        messages.error(request, "Sizning savatingiz bo‘sh!")
        return redirect("cart")

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.is_completed = False
            order.save()

           
            # for item in cart_items:
            #     OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity)

            request.user.cart.items.all().delete()
            
            messages.success(request, "Buyurtmangiz rasmiylashtirildi!")
            return redirect("order_history")

    else:
        form = CheckoutForm()
    
    return render(request, 'checkout.html', {'form': form, 'cart_items': cart_items})

def product_create(request):
    if request.user.is_staff:
        if request.method == 'POST':
            uid = request.POST.get('uid')
            info = request.POST.get('info')
            img_1 = request.FILES.get('img_1')
            # img_2 = request.FILES.get('img_2')
            # img_3 = request.FILES.get('img_3')
            product =  Product.objects.create(
                uid = int(uid),
                info = info
            )
            if img_1:
                img_1 = compress(img_1)
                product.image1 = img_1

            # if img_2:
            #     img_2 = compress(img_2)
            #     product.image2 = img_2

            # if img_3:
            #     img_3 = compress(img_3)
            #     product.image3 = img_3
            product.save()
            if product:
                messages.success(request, "Product q'shildi")
            else:
                messages.error(request, "Product yeratib bo'lmado")
        return render(request,'product-create.html')
    return redirect('/')
    