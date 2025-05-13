from .ajax import *
from django.urls import path
from .views import *


urlpatterns = [
    path('',Index, name='index'),
    path('filial/',filial_index),
    path('filial/order/',filial_order),
    path('filial/login/',filial_login),
    path('filial/logout/',filial_logout),
    path('filial/filial/',filial_filial),
    path('filial/registar/',filial_regisret ),
    path('filial/product-create/',product_create ),
    path("filial-order-status/<int:pk>/",update_order_status, name="update_order_status"),

    path('contact/',Contact),
    path('myaccount/',Myaccount),
    path('cart/',cart_view, name="cart"),
    path('checkout/',checkout_view, name='checkout'),
    path('wishlist/', wishlist_view, name='wishlist'),
    path('search/', search_products, name='search_products'),
    path('remove_from_cart/<int:item_id>/', DeleteProduct, name="delete"),
    path("add_to_cart/<int:product_id>/", add_to_cart, name="add_to_cart"),
    path('product/detail/<int:pk>/' , product_detail, name='product_detail'),
    path('toggle/<int:product_id>/', toggle_wishlist, name='toggle_wishlist'),
    path('product/add/<int:pk>/' , add_to_cart_detail, name='product_card_detail'),
    path("increase-quantity/<int:item_id>/", increase_quantity, name="increase_quantity"),
    path("decrease-quantity/<int:item_id>/", decrease_quantity, name="decrease_quantity"),
    path("payment/success/<int:order_id>/", payment_success, name="payment_success"),
    # path("payment/click/update/", ClickWebhookAPIView.as_view(), name="click_webhook"),
]