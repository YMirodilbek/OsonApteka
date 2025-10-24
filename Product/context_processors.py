from .models import OrderItem , Category
import json ,redis


def cart_context(request):
    cart_items = []
    cart_total = 0
    cart_count = 0
    result = []  

    if request.user.is_authenticated:
        try:
            cart_items = OrderItem.objects.filter(order__user=request.user, order__is_completed=False)
            for item in cart_items:
                result.append({
                    "id": item.product.id,
                    "name": item.product.info,
                    "price": float(item.price),
                    "qty": item.quantity,
                    "img": item.product.image1.url if item.product.image1 else '/static/media/default.jpg'
                })

            cart_total = sum(item.total_price for item in cart_items)
            cart_count = len(cart_items)
        except Exception as e:
            print(f"Error in cart_context: {e}")

    return {
        "cart_items": json.dumps(result if result else "wrong"),
        "cart_total": cart_total,
        "cart_count": cart_count,
    }

import redis
import json


r = redis.Redis(host='127.0.0.1', port=6379, db=0)

def category_contex(request=None):
    cache_key = 'category_context_data'
    
    # Redisdan ma'lumotlarni olish
    cached_data = r.get(cache_key)
    
    if cached_data:
        redis_data = True
        # Redisda ma'lumot bor bo'lsa
        categories = json.loads(cached_data)
    else:
        redis_data = False
        # Redisda yo'q bo'lsa, databasedan olish
        categories = list(Category.objects.prefetch_related('products').all().values('id', 'name'))
        # Redisga JSON formatida saqlash (1 soat = 3600 sekund)
        r.setex(cache_key, 3600*48, json.dumps(categories))
    
    return {"category_context": categories, "redis_data": redis_data}
