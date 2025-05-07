from django.db.models.functions import Collate
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
    import locale
    from operator import attrgetter

# Kirillcha alfavit uchun o'zbekcha yoki ruscha locale
    locale.setlocale(locale.LC_COLLATE, 'ru_RU.UTF-8')  # yoki 'uz_UZ.UTF-8' agar qo‘llasa

    category = sorted(Category.objects.all(), key=lambda x: locale.strxfrm(x.name))
    return{ "category":category}