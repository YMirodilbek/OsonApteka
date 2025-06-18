from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .viewsets import *

router = DefaultRouter()
router.register(r'apteka', OurPharmacieViewSet, basename='apteka')
router.register(r'product', ProductViewSet, basename='product')

urlpatterns = [
    # Agar boshqa viewlar bo'lsa, shu yerga yoziladi
]


urlpatterns += router.urls
