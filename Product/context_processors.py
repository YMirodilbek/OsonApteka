from .models import OrderItem , Category


def cart_context(request):
    cart_items = []
    cart_total = 0

    if request.user.is_authenticated:
        cart_items = OrderItem.objects.filter(order__user=request.user, order__is_completed=False)

        # Endi `total_price_per_item` ni ishlatish shart emas, chunki modelning `total_price` propertysi bor
        cart_total = sum(item.total_price for item in cart_items)
    return {
        "cart_items": cart_items,
        "cart_total": cart_total,  # Savatning umumiy narxi
    }


def category_contex(request):
     category = Category.objects.all()
     return{ "category":category}