from django.conf.urls import handler404,handler500
from Admin.views import handler_404, handler_500
from django.conf.urls.static import static
from django.urls import path,include
from django.contrib import admin
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('jet/', include('jet.urls', 'jet')), 
    path('auth/',include('main.urls')),
    path('',include('Product.urls')),
    path('front/',include('tmp.urls'))
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404=handler_404
handler500=handler_500

