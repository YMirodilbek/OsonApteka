from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from click_up.views import ClickWebhook
from django.contrib.auth import  login ,logout
from django.contrib import messages
from django.shortcuts import render
from .lotin_krill import compress
from django.conf import settings
from unidecode import unidecode
from click_up import ClickUp
from .decorator import *
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
    per_page_classes = 5
    per_class_limit = 30

    grouped_data_json = r.get('products_by_class')
    if not grouped_data_json:
        return render(request, 'index.html', {"data": []})

    grouped_by_class = json.loads(grouped_data_json)

    result = []

    # Agar category tanlangan bo‘lsa, faqat o‘sha category qaytariladi
    if category:
        category = category
        products = (
            grouped_by_class.get(category)
        )

        if products and len(products) > 0:
            result = [{"class_name": category, "products": products[:per_class_limit]}]
        else:
            result = []  # bo‘sh list qaytadi
    else:
        # Aks holda barcha classlarni paginate qilib olish
        filtered_classes = [
            class_name for class_name, items in grouped_by_class.items()
            if len(items) > 0
        ]
        paginator = Paginator(filtered_classes, per_page_classes)
        selected_classes = paginator.page(page).object_list

        for class_name in selected_classes:
            items = grouped_by_class[class_name][:per_class_limit]
            result.append({"class_name": class_name, "products": items})

        context = {
            "data": result,
            "current_page": page,
            "total_pages": paginator.num_pages,
            "blogs": Blog.objects.all().order_by('-id')[:5]
        }
        return render(request, 'index.html', context)

    return render(request, 'index.html', {"data": result})


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
    price = int(request.GET.get('price',0))
    product = get_object_or_404(Product, id=pk)
    r = redis.Redis(host='localhost', port=6379, db=0)
    result = r.get('final_result') 
    if result:
        result = json.loads(result.decode('utf-8'))
    
    
    result_dict = {item['id']: item for item in result}
    name = result_dict.get(pk, {}).get('name', '')

    order, created = Order.objects.get_or_create(user=request.user, is_completed=False)
    order_item, created = OrderItem.objects.get_or_create(
                                    order=order,      
                                    product=product,
                                    price =price,
                                    name = name,
                                    defaults={'quantity':quantity}
                                    )

    if not created:
        order_item.quantity += quantity
        order_item.save()
    return redirect(f'/product/detail/{pk}')


class ClickWebhookAPIView(ClickWebhook):
    def successfully_payment(self, params):
        """
        Handle successful payments from Click
        """
        merchant_trans_id = params.get('merchant_trans_id')
        try:
            order = Order.objects.get(id=merchant_trans_id)
            order.is_paid = True
            order.save()
            # Here you can handle additional order processing
            # For example, send email notification, create shipping order, etc.
        except Order.DoesNotExist:
            pass
        
    def cancelled_payment(self, params):
        """
        Handle cancelled payments from Click
        """
        merchant_trans_id = params.get('merchant_trans_id')
        try:
            order = Order.objects.get(id=merchant_trans_id)
            # Handle cancelled payment 
            # For example, mark the order as cancelled or notify admin
        except Order.DoesNotExist:
            pass


def payment_success(request, order_id):
    """
    Display payment success page after successful Click payment
    """
    try:
        order = Order.objects.get(id=order_id, user=request.user)
        return render(request, 'payment_success.html', {'order': order})
    except Order.DoesNotExist:
        messages.error(request, "Buyurtma topilmadi!")
        return redirect('order_history')


def checkout_view(request):
    order = Order.objects.filter(user=request.user, is_completed=False).first()
    if not order or not order.items.exists():
        messages.error(request, "Sizning savatingiz bo'sh!")
        return redirect("cart")
    
    cart_items = order.items.all()
    
    filials = Filial.objects.all()
    if not filials.exists():
        default_filial = Filial.objects.create(
            name="Markaziy Filial",
            address="Toshkent sh., Yunusobod tumani"
        )
        filials = Filial.objects.all()  

    if request.method == 'POST':
        form = CheckoutForm(request.POST, instance=order)
        if form.is_valid():
            order = form.save(commit=False)
            
            address_type = request.POST.get('address_type')
            if address_type == 'maps':
                lat = request.POST.get('address_lat')
                lng = request.POST.get('address_lng')
                if lat and lng:
                    order.address_text = f"Latitude: {lat}, Longitude: {lng}"
            
            order.is_completed = True
            order.save()
            
            if order.payment_method == 'click':
                click_up = ClickUp(
                    service_id=settings.CLICK_SERVICE_ID,
                    merchant_id=settings.CLICK_MERCHANT_ID
                )
                
                return_url = request.build_absolute_uri(f'/payment/success/{order.id}/')
                payment_link = click_up.initializer.generate_pay_link(
                    id=order.id,
                    amount=order.total_price + 15000,  
                    return_url=return_url
                )
                
                return redirect(payment_link)
            
            messages.success(request, "Buyurtmangiz rasmiylashtirildi!")
            return redirect("order_history")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")

    else:
        form = CheckoutForm(instance=order)
    
    context = {
        'form': form, 
        'cart_items': cart_items, 
        'order': order,
        'filials': filials  
    }
    
    return render(request, 'checkout.html', context)


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


@is_staff
def product_create(request):
    if request.method == 'POST':
        uid = request.POST.get('uid')
        info = request.POST.get('info')
        img_1 = request.FILES.get('img_1')
        product =  Product.objects.create(
            uid = int(uid),
            info = info
        )
        if img_1:
            img_1 = compress(img_1)
            product.image1 = img_1

        product.save()
        if product:
            messages.success(request, "Product q'shildi")
        else:
            messages.error(request, "Product yeratib bo'lmado")
    return render(request,'filial/product-create.html')


@is_staff
def filial_index(request):
    return render(request,'filial/index.html' )


@is_staff
def filial_order(request):

    filial_id = request.GET.get('filial-id')
    type_choices = Order.TYPE_CHOICES
    filials = request.user.filials.all()
    orders_by_filial = {}

    if filial_id:
        selected_filial = get_object_or_404(Filial, id=filial_id)
        orders = Order.objects.filter(filial=selected_filial, is_active=True).order_by('-id')
        page_number = request.GET.get(f'page_{selected_filial.id}')
        paginator = Paginator(orders, 2)
        page_obj = paginator.get_page(page_number)
        orders_by_filial[selected_filial] = page_obj

    elif request.user.is_superuser:
        selected_filials = Filial.objects.all()
        for filial in selected_filials:
            orders = Order.objects.filter(filial=filial, is_active=True).order_by('-id')
            page_number = request.GET.get(f'page_{filial.id}')
            paginator = Paginator(orders, 2)
            page_obj = paginator.get_page(page_number)
            orders_by_filial[filial] = page_obj

    else:
        for filial in filials:
            orders = Order.objects.filter(filial=filial, is_active=True).order_by('-id')
            page_number = request.GET.get(f'page_{filial.id}')
            paginator = Paginator(orders, 2)
            page_obj = paginator.get_page(page_number)
            orders_by_filial[filial] = page_obj

    orders =  Order.objects.all()

    context = {
        'orders_by_filial': orders_by_filial,
        'type_choices': type_choices
    }
    return render(request, 'filial/order.html', context)



@is_staff
def filial_filial(request):
    filial = Filial.objects.all()
    return render(request,'filial/filial.html',  {"filial":filial})


@is_staff
def filial_regisret(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        name = request.POST.get('name')
        address = request.POST.get('address')
        user =  CustomUser.objects.create(
            phone_number=username,
            password=password,
            is_staff = True
        )
        filial  = Filial.objects.create(
                                        name=name,
                                        address=address
                                        )
        filial.users.set([user])
    return render(request,'filial/filial-register.html' )


def filial_logout(request):
    logout(request)
    return redirect('/filial/login')


def filial_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            user = CustomUser.objects.get(phone_number=username)

            if user.check_password(password):
                login(request, user)
                return redirect('/filial/')  
            else:
                messages.error(request, "Parol noto‘g‘ri.")
        except CustomUser.DoesNotExist:
            messages.error(request, "Foydalanuvchi topilmadi.")
    
    return render(request, 'filial/login.html')


