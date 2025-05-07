from .ajax import add_to_cart,  search_products
from django.urls import path
from .views import *


urlpatterns = [
    path('',Index),
    path('contact/',Contact),
    path('myaccount/',Myaccount),
    path('cart/',cart_view, name="cart"),
    path('checkout/',checkout_view, name='checkout'),
    path('wishlist/', wishlist_view, name='wishlist'),
    path('search/', search_products, name='search_products'),
    path('product-create/',product_create , name="product-create"),
    path('remove_from_cart/<int:item_id>/', DeleteProduct, name="delete"),
    path("add_to_cart/<int:product_id>/", add_to_cart, name="add_to_cart"),
    path('product/detail/<int:pk>/' , product_detail, name='product_detail'),
    path('toggle/<int:product_id>/', toggle_wishlist, name='toggle_wishlist'),
    path('product/add/<int:pk>/' , add_to_cart_detail, name='product_card_detail'),
    path("increase-quantity/<int:item_id>/", increase_quantity, name="increase_quantity"),
    path("decrease-quantity/<int:item_id>/", decrease_quantity, name="decrease_quantity"),
    # path("checkout/", checkout, name="checkout"),
]