from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Sum, F, Prefetch , Count , Q
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator ,EmptyPage
from django.db.models.functions import TruncDay
from django.contrib.auth import  login ,logout
from datetime import datetime, timedelta
from click_up.views import ClickWebhook
from django.http import JsonResponse
from django.shortcuts import render
from collections import OrderedDict
from django.contrib import messages
from .lotin_krill import compress
from django.conf import settings
from click_up import ClickUp
from tmp.models import *
from .decorator import *
from .models import *
from .forms import  *
import logging
import redis
import json
import os

logger = logging.getLogger('Product')


@login_required(login_url='/auth/send-otp/')
def cart_view(request):
    order = Order.objects.filter(user=request.user, is_completed=False).select_related('filial').prefetch_related('items','items__product').first()
    return render(request, "cart.html", {"order": order})


@login_required(login_url='/auth/send-otp/')
def cart_view_json(request):
    cart_items = []
    cart_total = 0
    cart_count = 0

    if request.user.is_authenticated:
        result = []
        try:
            cart_items = OrderItem.objects.filter(order__user=request.user, order__is_completed=False)
            for item in cart_items:
                result.append({
                    "id": item.id,
                    "product_id": item.product.id,
                    "name": item.product.name,
                    "price": float(item.price),
                    "qty": item.quantity,
                    "img": item.product.image1.url if item.product.image1 else '/static/media/default.jpg'
                })

            cart_total = sum(item.total_price for item in cart_items)
            cart_count = len(cart_items)
        except Exception as e:
            logger.error(f"Error in cart_context: {e}")


    return JsonResponse({"cart_items": result, "cart_total": cart_total, "cart_count": cart_count, "status":200})


def Index(request):
    category_name = request.GET.get('category')
    page = request.GET.get("page", 1)

    try:
        page = int(page)
    except (TypeError, ValueError):
        page = 1

    product_price_qs = ProductPrice.objects.filter(price__gt=0, amount__gt=0)

    products_qs = Product.objects.filter(
        product_prise__in=product_price_qs,  
        name__isnull=False
    ).exclude(name='').order_by('id').distinct().select_related('category', 'member').prefetch_related(
        Prefetch('product_prise', queryset=product_price_qs, to_attr='prices')
    )

    categories_qs = Category.objects.annotate(
        product_count=Count('products', filter=Q(products__in=products_qs))
    ).filter(product_count__gt=0)

    if category_name:
        categories_qs = categories_qs.filter(name=category_name)

    categories_qs = categories_qs.prefetch_related(
        Prefetch('products', queryset=products_qs, to_attr='filtered_products_all')
    )

    paginator = Paginator(categories_qs, 5)
    try:
        page_obj = paginator.get_page(page)
    except EmptyPage:
        page_obj = paginator.get_page(1)

    for category in page_obj:
        category.filtered_products = category.filtered_products_all[:50]

    context = {
        "page": page,
        "paginator": page_obj,
        "blogs": Blog.objects.all().order_by('-id')[:4]
    }
    return render(request, 'index.html', context)


@login_required(login_url='/auth/send-otp/')
def increase_quantity(request, item_id):
    """Mahsulot miqdorini oshirish"""
    order_item = get_object_or_404(OrderItem, id=item_id, order__user=request.user, order__is_completed=False)
    order_item.quantity += 1
    order_item.save()
    return cart_view_json(request)


@login_required(login_url='/auth/send-otp/')
def decrease_quantity(request, item_id):
    """Mahsulot miqdorini kamaytirish (0 ga yetganda o‘chirish)"""
    order_item = get_object_or_404(OrderItem, id=item_id, order__user=request.user, order__is_completed=False)

    if order_item.quantity > 1:
        order_item.quantity -= 1
        order_item.save()
    else:
        order_item.delete()
    return cart_view_json(request)


@login_required(login_url='/auth/send-otp/')
def DeleteProduct(request, item_id):
    """ Savatdan bitta mahsulot turini butunlay o‘chirish """
    # order = Order.objects.filter(user=request.user, is_completed=False)
    order_item = OrderItem.objects.get(id=item_id)
    if order_item:
        order_item.delete()
    return cart_view_json(request)


def product_detail(request, pk):
    product = Product.objects.get(id=int(pk))

    raw_prices = product.product_prise.filter(price__gt=0).order_by('price')

    seen_prices = OrderedDict()
    for p in raw_prices:
        if p.price not in seen_prices:
            seen_prices[p.price] = p

    unique_prices = list(seen_prices.values())

    context = {
        "prices": unique_prices,
        "product": product
    }
    return render(request, 'product-details.html', context)


@login_required(login_url='/auth/send-otp/')
def add_to_cart_detail(request,pk):
    quantity = int(request.GET.get('quantity',1))
    price = int(request.GET.get('price',0))
    product = get_object_or_404(Product, id=pk)
    if product.product_type == "Рецепт билан":
        messages.error(request, F"{product.name} Рецептурный")
        return redirect(f'/product/detail/{pk}')

    order = Order.objects.filter(user=request.user, is_completed=False).first()

    if not order:
        order = Order.objects.create(user=request.user, is_completed=False)
    order_item, created = OrderItem.objects.get_or_create(
                                    order=order,
                                    product=product,
                                    price =price,
                                    name = product.name,
                                    defaults={'quantity':quantity}
                                    )

    if not created:
        order_item.quantity += quantity
        order_item.save()
    return redirect(f'/product/detail/{pk}')


class ClickWebhookAPIView(ClickWebhook):
    def validate_fiscal_item(self, fiscal_item):
        """
        Validate that fiscal item has all required fields for Click
        """
        required_fields = ['Name', 'SPIC', 'PackageCode', 'Price', 'VAT', 'VATPercent']

        if not all(field in fiscal_item for field in required_fields):
            return False

        if not fiscal_item.get('Name') or fiscal_item.get('Name').strip() == '':
            return False

        return True

    def get_fiscal_items_for_account(self, account):

        try:
            logger.info(f"Generating fiscal items for order {account.id}")
            order = Order.objects.get(id=account.id)
            fiscal_items = []

            for item in order.items.all():
                
                product_price = item.product.product_prise.first()

                if product_price:
                    fiscal_item = product_price.fiscal_items.copy()
                    fiscal_item["Amount"] = item.quantity

                    if self.validate_fiscal_item(fiscal_item):
                        fiscal_items.append(fiscal_item)
                        logger.debug(f"Added complete fiscal item: {fiscal_item.get('Name')}")
                    else:
                        logger.warning(f"Skipped incomplete fiscal item for product {item.product.id}: {fiscal_item.get('Name', 'Unknown')}")
                else:
                    logger.warning(f"No ProductPrice found for product {item.product.id}")

            if fiscal_items:
                logger.info(f"Generated {len(fiscal_items)} complete fiscal items for order {account.id}")
            else:
                logger.warning(f"No complete fiscal items found for order {account.id} - returning empty list")

            logger.debug(f"Final fiscal items: {fiscal_items}")
            return fiscal_items

        except Order.DoesNotExist:
            logger.error(f"Order with ID {account.id} does not exist")
            return []

        except Exception as e:
            logger.error(f"Error getting fiscal items for account {account}: {e}")
            return []

    
    
    def successfully_payment(self, params):
        """
        Handle successful payments from Click
        """
        logger.info(f"Successfully payment received - incoming params: {params}")

        order_id = getattr(params, 'merchant_trans_id', None)

        if order_id:
            try:
                order = Order.objects.get(id=int(order_id))
                order.is_paid = True
                order.save()
                from main.bot_messages import send_telegram_message
                telegram_ids = (order.filial.users.values_list('telegram_id', flat=True))
                for i in telegram_ids:
                    send_telegram_message(
                        telegram_id=i,
                        message=f"🆔 ид: {order.id}\n"
                                f"⏰ соат : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                                f"🏢 филиал : {order.filial}\n"
                                f"💰 сумма: {order.total_price} сум\n"
                                f"📞 тел: {order.phone_number1}\n"
                                f"💊 дорилар сони: {order.items.all().count()} та\n"
                                f"📍 Адрес: {order.address_text} \n"
                                f"💳 тўлов : {'бажатилди' if order.is_paid else 'кутиламоқда'}"
                                                    )
                logger.info(f"Order {order_id} marked as paid successfully")

            except Order.DoesNotExist:
                logger.error(f"Order {order_id} not found")
            except Exception as e:
                logger.error(f"Error updating order {order_id}: {str(e)}")
        else:
            logger.error("No order ID found in payment params")

    def cancelled_payment(self, params):
        """
        Handle cancelled payments from Click
        """
        logger.warning(f"Payment cancelled - incoming params: {params}")

        order_id = getattr(params, 'merchant_trans_id', None)

        if order_id:
            try:
                order = Order.objects.get(id=int(order_id))
                order.is_paid = False
                order.save()

                logger.warning(f"Order {order_id} marked as payment cancelled")

            except Order.DoesNotExist:
                logger.error(f"Order {order_id} not found")
            except Exception as e:
                logger.error(f"Error updating cancelled order {order_id}: {str(e)}")
        else:
            logger.error("No order ID found in cancellation params")


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
    logger.info(f"Checkout process started for user: {request.user.phone_number}")

    dostaff = 0
    dostafca = Dostafca.objects.last()
    if dostafca and dostafca.amount:
        dostaff = dostafca.amount

    order = Order.objects.filter(user=request.user, is_completed=False).first()
    if not order or not order.items.exists():
        logger.warning(f"Empty cart for user: {request.user.phone_number}")
        messages.error(request, "Sizning savatingiz bo'sh!")
        return redirect("cart")

    logger.info(f"Using existing cart order for checkout - user: {request.user.phone_number}, order ID: {order.id}")
    cart_items = order.items.all()

    filials = Filial.objects.all()
    if not filials.exists():
        default_filial = Filial.objects.create(
            name="Markaziy Filial", 
            address="Toshkent sh., Yunusobod tumani"
        )
        filials = Filial.objects.all()

    if request.method == 'POST':
        filial_id = int(request.POST.get('filial'))

        logger.info(f"Processing checkout form for order ID: {order.id}")

        form = CheckoutForm(request.POST, instance=order)
        if form.is_valid():
            order = form.save(commit=False)

            address_type = request.POST.get('address_type')
            if address_type == 'maps':
                lat = request.POST.get('address_lat')
                lng = request.POST.get('address_lng')
                if lat and lng:
                    order.address_text = f"Latitude: {lat}, Longitude: {lng}"

            filial = Filial.objects.get(id=filial_id)
            order.filial = filial
            order.is_completed = True
            order.save()

            logger.info(f"Order {order.id} completed successfully for user: {request.user.phone_number}")

            if order.payment_method == 'click':
                logger.info(f"Processing Click payment for order {order.id}, amount: {order.amount}")
                click_up = ClickUp(
                    service_id=settings.CLICK_SERVICE_ID,
                    merchant_id=settings.CLICK_MERCHANT_ID
                )

                return_url = request.build_absolute_uri(f'/payment/success/{order.id}/')
                payment_link = click_up.initializer.generate_pay_link(
                    id=order.id,
                    amount=order.amount,
                    return_url=return_url
                )

                logger.info(f"Click payment link generated for order {order.id}: {payment_link}")
                return redirect(payment_link)

            logger.info(f"Processing non-Click payment for order {order.id}, method: {order.payment_method}")
            from main.bot_messages import send_telegram_message
            telegram_ids = (order.filial.users.values_list('telegram_id', flat=True))
            for i in telegram_ids:
                send_telegram_message(
                        telegram_id=i,
                        message=f"🆔 ид: {order.id}\n"
                                f"⏰ соат : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                                f"🏢 филиал : {order.filial}\n"
                                f"💰 сумма: {order.total_price} сум\n"
                                f"📞 тел: {order.phone_number1}\n"
                                f"💊 дорилар сони: {order.items.all().count()} та\n"
                                f"📍 Адрес: {order.address_text} \n"
                                f"💳 тўлов : {'бажатилди' if order.is_paid else 'кутиламоқда'}"
                                                    )
            logger.info(f"Telegram notifications sent for order {order.id}")
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
        'filials': filials,
        'dostaff': dostaff,
        'total_sum': order.total_price
    }

    return render(request, 'checkout.html', context)


@login_required(login_url='/auth/send-otp/')
def Myaccount(request):
    orders = Order.objects.filter(user=request.user).order_by('-id')
    if request.GET.get('order-id'):
        order = Order.objects.get(id=request.GET.get('order-id'))
        order_items =  OrderItem.objects.filter(order=order)
        order_items_list = []
        for item in order_items:
            order_items_list.append({
                'id': item.id,
                'name': item.name,
                'quantity': item.quantity,
                'price': item.price,
                'total_price': item.total_price,
                'product': item.product.info,
                'product_id': item.product.id,
                'product_image': item.product.image1.url if item.product.image1 else '/static/media/default.jpg'
            })
        return  JsonResponse(order_items_list, safe=False)

    wishlist_items = Wishlist.objects.filter(user=request.user)

    context = {
        'orders': orders,
        'wishlist_items': wishlist_items
    }

    return render(request, 'profile.html', context)


@login_required(login_url='/auth/send-otp/')
def toggle_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist_item = Wishlist.objects.filter(user=request.user, product=product)

    if wishlist_item.exists():
        wishlist_item.delete()
        messages.success(request, "Mahsulot wishlistdan olib tashlandi!")
    else:
        Wishlist.objects.create(user=request.user, product=product)
        messages.success(request, "Mahsulot wishlistga qo‘shildi!")

    return redirect(request.META.get('HTTP_REFERER', '/'))


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
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            
            # Rasmni forma ichida siqib olish
            if 'image1' in request.FILES:
                product.image1 = compress(request.FILES['image1'])
            
            product.save()
            messages.success(request, 'Mahsulot muvaffaqiyatli qo\'shildi!')
            return redirect('/filial/product-create/')
    else:
        form = ProductForm()
    
    filials = Filial.objects.all()
    return render(request,'filial/product-create.html', {'filials':filials ,'form': form})


@is_staff
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        form = Product_editForm(request.POST, instance=product)  # FILES parametrini olib tashlang
        if form.is_valid():
            form.save()
            return redirect(f'/filial/product-edit/{product_id}/')
    else:
        form = Product_editForm(instance=product)
    
    return render(request, 'filial/edit_product.html', {
        'form': form,
        'product': product
    })


def edit_product_image(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        new_image = request.FILES.get('image1')
        if new_image:
            if product.image1:
                try:
                    os.remove(product.image1.path)
                except:
                    pass
            product.image1 = new_image
            product.save()
            return redirect('/filial/products/')
    
    return render(request, 'filial/edit_image.html', {'product': product})


@is_staff
def products(request):
    page_number = request.GET.get('page')
    product = Product.objects.all().order_by('id')
    paginator = Paginator(product, 50 )
    page_obj = paginator.get_page(page_number)
    member = Member.objects.all()
    return render (request, 'filial/product.html', {"page_obj":page_obj,'member':member})


@is_staff
def filial_index(request):
    filial_id = request.GET.get('filial-id')
    filials = request.user.filials.all()

    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)

    user_count = CustomUser.objects.filter(is_staff=False).count()
    user_count_active = CustomUser.objects.filter(is_staff=False, last_login__gte=start_date).count()

    result = []
    count = 0
    count_now = 0

    if filial_id:
        filial_filter = {'filial_id': filial_id}
    elif request.user.is_superuser:
        filial_filter = {}
    else:
        filial_filter = {'filial__in': filials}

    # Buyurtmalar va kunlik savdolar
    orders = Order.objects.filter(
        is_active=True,
        is_paid=True,
        **filial_filter
    ).select_related('filial').prefetch_related('items').annotate(
        day=TruncDay('created_at')
    ).values('day').annotate(
        total_amount=Sum(F('items__price') * F('items__quantity'))
    ).order_by('day')

    counts = Order.objects.aggregate(
    count=Count('id', filter=Q(is_paid=True, **filial_filter)),
    count_now=Count('id', filter=Q(is_paid=True, created_at__date=end_date.date(), **filial_filter))
    )
    count = counts['count']
    count_now = counts['count_now']
    # daily_summary = orders

    for entry in orders:
        result.append({
            'date': entry['day'].strftime('%Y-%m-%d'),
            'amount': int(entry['total_amount'] or 0)
        })
    filials = Filial.objects.all()
    context = {   
        'count': count,
        'filials':filials,
        'count_now': count_now,
        'user_count': user_count,
        'result': json.dumps(result),
        'user_count_active': user_count_active,
    }
    return render(request,'filial/index.html',context )


@is_staff
def filial_order(request):

    filial_id = request.GET.get('filial-id')
    type_choices = Order.TYPE_CHOICES
    filials = request.user.filials.all()
    orders_by_filial = {}


    if filial_id:
        selected_filial = get_object_or_404(Filial, id=filial_id)
        orders = Order.objects.filter(filial=selected_filial, is_active=True).order_by('-id').select_related(
                'filial'
            ).prefetch_related(Prefetch('items', queryset=OrderItem.objects.select_related('product')))
        page_number = request.GET.get(f'page_{selected_filial.id}')
        paginator = Paginator(orders, 50    )
        page_obj = paginator.get_page(page_number)
        orders_by_filial[selected_filial] = page_obj


    elif request.user.is_superuser:
        selected_filials = Filial.objects.all()
        for filial in selected_filials:
            orders = Order.objects.filter(filial=filial, is_active=True).order_by('-id').select_related(
                'filial'
            ).prefetch_related(Prefetch('items', queryset=OrderItem.objects.select_related('product')))
            page_number = request.GET.get(f'page_{filial.id}')
            paginator = Paginator(orders, 50)
            page_obj = paginator.get_page(page_number)
            orders_by_filial[filial] = page_obj
    else:
        for filial in filials:
            orders = Order.objects.filter(filial=filial, is_active=True).order_by('-id').select_related(
                'filial'
            ).prefetch_related(Prefetch('items', queryset=OrderItem.objects.select_related('product')))
            page_number = request.GET.get(f'page_{filial.id}')
            paginator = Paginator(orders, 50)
            page_obj = paginator.get_page(page_number)
            orders_by_filial[filial] = page_obj

    # orders =  Order.objects.all()
    filials = Filial.objects.all()
    context = {
        'filials':filials,
        'type_choices': type_choices,
        'orders_by_filial': orders_by_filial,
    }
    return render(request, 'filial/order.html', context)


@is_staff
def filial_filial(request):
    filial = Filial.objects.all()
    return render(request,'filial/filial.html',  {"filials":filial})


@is_staff
def filial_regisret(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        telegram_id = int(request.POST.get('telegram_id'))
        name = request.POST.get('name')
        address = request.POST.get('address')
        user =  CustomUser.objects.create_user(
            phone_number=username,
            password=password,
            is_staff = True,
            telegram_id = telegram_id,
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


@is_staff
def filial_users(request):
    users = CustomUser.objects.filter(is_staff = False).order_by('-id').prefetch_related(
                    Prefetch(
                        'orders',
                        queryset=Order.objects.order_by('-created_at'),
                        to_attr='prefetched_orders'
                    )
                )
    return render(request, 'filial/users.html', {'users':users})


def member_view(request):
    members  = Member.objects.all().order_by('-id')
    return render (request,'filial/member.html', {"members":members})

def filial_order_client(request):
    client_id = request.GET.get('client-id')
    # filial_id = request.GET.get('filial-id')
    # orders_by_filial = {}
    if client_id:
        orders = Order.objects.filter(user_id=int(client_id) , is_active=True).order_by('-id').select_related(
            'filial'
        ).prefetch_related(Prefetch('items', queryset=OrderItem.objects.select_related('product')))
    return render(request, 'filial/user-order.html',{'orders':orders})