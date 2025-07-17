from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter
from django.urls import path
from .viewsets import *
from .views import *
from django.views.generic import TemplateView
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

router = DefaultRouter()
router.register(r'apteka', OurPharmacieViewSet, basename='apteka')
router.register(r'search', SearchProductViewSet, basename='search')
router.register(r'products', CategoryProductsViewSet, basename='product')
router.register(r'wishlist', WishlistViewSet, basename='wishlist')
router.register(r'member', MemberViewset, basename='member')
router.register(r'order', OrderViewset, basename='order')
router.register(r'blog', BlogViewset, basename='blog')




schema_view = get_schema_view(
   openapi.Info(
      title="api",
      default_version='v1',
      description="API hujjatlari",
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)


    

urlpatterns = [
    path('swagger.json/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('swagger-ui/', TemplateView.as_view(template_name='swagger_ui.html'), name='swagger-ui'),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),



    path('user-update/', user_update),
    path('get-user/', get_user),
    path('phone-number/', phone_number_api),
    path('login/', login_api),
    path('category/', get_category),
    path('category/<int:pk>', category),
    path('dastafca/', get_dastafca),
    path('filial/', get_filial),
]

urlpatterns += router.urls

