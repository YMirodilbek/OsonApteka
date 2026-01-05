from django.urls import path
from .views import *
from .ajax import *



urlpatterns = [
    path('download-excel/', download_products_excel, name='download_products_excel'),
    path('uslugi', uslugi, ),
    path('dogovor', dogovor, ),
    path('document', document, ),
    path('dastafca/', dastafca, ),
    
    path('filial/',filial_index , name= 'filial_index'),
    path('filial/products/',products),
    path('filial/order/',filial_order),
    path('filial/login/',filial_login),
    path('filial/users/',filial_users),
    path('filial/logout/',filial_logout),
    path('filial/filial/',filial_filial),
    path('filial/registar/',filial_regisret ),
    path('filial/product-create/',product_create ),
    path('filial/order-client/',filial_order_client),
    path('filial/api/product-search/',product_search_api ),
    path('filial/product-delete/<int:pk>/',delete_product),
    path('filial/product-edit/<int:product_id>/', edit_product),
    path('filial/edit_product_image/<int:product_id>/', edit_product_image),
    path('filial-product-person-edit/', update_person),
    path("filial-order-status/<int:pk>/",update_order_status, name="update_order_status"),
    path("filial-member/",member_view, name="member"),
    
    path('glavni/', glavniimg, name='glavni_list'),
    path('glavni/delete/<int:pk>/',delete_glavni, name='delete_glavni'),
    path('add/',glavni_add, name='glavni_add'),
    
    # path("filial-category/",category_img_edit, name="category_img"),
    path("filial-category/",category_img_edit, name="category_img_edit"),
    path("filial-add-member/",add_product_member, name="add_product_member"),
    path("member/create/",member_create, name="member_create"),
    path("member/delete/<int:pk>/",member_delete, name="member_delete"),

    path("chat_web/",chat_web, name="create_chat_web"),
    path("get-messages/<int:user_id>/",get_messages, name="get_messages"),
    # urls.py

    path('chta/image/create/', send_image, name='send_image'),
    path('chat/message/create/', send_text, name='send_text'),

    # path('chat/get-users/', get_recent_users, name='get_recent_users'),

    
    path('',Index, name='index'),
    path('contact/',Contact),
    path('myaccount/',Myaccount, name='myaccount'),
    path('cart/',cart_view, name="cart"),
    path('cart-json/',cart_view_json, name="cart_json"),
    path('checkout/',checkout_view, name='checkout'),
    path('search/', search_products, name='search_products'),
    path('remove_from_cart/<int:item_id>/', DeleteProduct, name="delete"),
    path("add_to_cart/<int:product_id>/", add_to_cart, name="add_to_cart"),
    path('product/detail/<int:pk>/' , product_detail, name='product_detail'),
    path('toggle/<int:product_id>/', toggle_wishlist, name='toggle_wishlist'),
    path('product/add/<int:pk>/' , add_to_cart_detail, name='product_card_detail'),
    path("increase-quantity/<int:item_id>/", increase_quantity, name="increase_quantity"),
    path("decrease-quantity/<int:item_id>/", decrease_quantity, name="decrease_quantity"),
    path("payment/success/<int:order_id>/", payment_success, name="payment_success"),
    path("payment/click/update/", ClickWebhookAPIView.as_view(), name="click_webhook"),
]
