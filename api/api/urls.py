from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

from drf_spectacular.views import (
    SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path(
        'schema/swagger-ui/', 
        SpectacularSwaggerView.as_view(), 
        name='swagger-ui'
    ),
    path(
        'schema/redoc/', 
        SpectacularRedocView.as_view(), 
        name='redoc'
    ),
    path('', include('packing.urls')), 
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
