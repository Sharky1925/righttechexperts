from django.urls import path

from headless import views

app_name = 'headless'

urlpatterns = [
    path('health', views.health, name='health'),
    path('headless/export', views.headless_export, name='headless_export'),
    path('headless/sync', views.headless_sync_upsert, name='headless_sync_upsert'),
    path('delivery', views.delivery_index, name='delivery_index'),
    path('delivery/page/<slug:slug>', views.acp_delivery_page, name='acp_delivery_page'),
    path('delivery/dashboard/<str:dashboard_id>', views.acp_delivery_dashboard, name='acp_delivery_dashboard'),
    path('delivery/theme/<str:token_set_key>', views.acp_delivery_theme, name='acp_delivery_theme'),
    path(
        'delivery/content/<str:content_type_key>/<str:entry_key>',
        views.acp_delivery_content_entry,
        name='acp_delivery_content_entry',
    ),
]
