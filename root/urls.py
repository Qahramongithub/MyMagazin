from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from root import settings

urlpatterns = ([
    path('admin/', admin.site.urls),

    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/', include('apps.urls')),
    path('house/', include('house.urls')),
])

if not settings.DEBUG:
    (urlpatterns + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
     + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT))
handler404 = 'apps.views.errors.handler404'
handler500 = 'apps.views.errors.handler500'
