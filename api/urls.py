from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.routers import DefaultRouter
from django.views.generic import TemplateView
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from django.urls import path
from drf_yasg import openapi
from .viewsets import *
from .views import *

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

   path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
   path('checkout/',CheckoutAPIView.as_view(), name='checkout_api'),

  
   path('user-update/', user_update),
   path('get-user/', get_user),
   path("get-person/", get_person_status),
   path("person/", person),
   path('phone-number/', phone_number_api),
   path('login/', LoginAPIView.as_view(), name='jwt_login'),
   path('category/', get_category),
   path('category/<int:pk>', category),
   path('dastafca/', get_dastafca),
   path('product-order/', product_order),
   path('filial/', get_filial),
]

urlpatterns += router.urls

