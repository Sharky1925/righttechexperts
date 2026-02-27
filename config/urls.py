from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

urlpatterns = [
    path('', include(('public.urls', 'public'), namespace='public')),
    path('admin/acp/', include(('acp.urls', 'acp'), namespace='acp')),
    path('admin/', include(('admin_panel.urls', 'admin'), namespace='admin')),
    path('api/', include(('headless.urls', 'headless'), namespace='headless')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
