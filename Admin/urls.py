from django.conf.urls import handler404,handler500
from Admin.views import handler_404, handler_500
from django.urls import path,include , re_path
from django.conf.urls.static import static
from django.contrib import admin
from django.conf import settings



urlpatterns = [
    
    # path('api/swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    # path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('admin/', admin.site.urls), 
    path('',include('Product.urls')),
    path('auth/',include('main.urls')),
    path('front/',include('tmp.urls')),
    path('api/',include('api.urls')),
   
    
    # path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


handler500=handler_500
handler404=handler_404

