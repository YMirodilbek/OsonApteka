from .models import OrderItem , Category
import json

def cart_context(request):
    cart_items = []
    cart_total = 0
    cart_count = 0

    if request.user.is_authenticated:
        result = []
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


def category_contex(request):
    category = Category.objects.all()   
    return {"category_context":category}