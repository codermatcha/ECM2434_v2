from django.contrib import admin
from django.http import JsonResponse
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
def api_config(request):
    is_prod = request.get_host() == 'caffeinated-divas.fly.dev'
    return JsonResponse({
        "apiBaseUrl": "/api",
        "mediaBaseUrl": "/media",
        "environment": "production" if is_prod else "development"
    })
urlpatterns = [
    path('api-config/', api_config, name='api_config'),
    path('admin/', admin.site.urls),
    path('api/', include('bingo.urls')),
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
]

urlpatterns += [
    re_path(r'^(?!admin/|api/|static/|media/).*$', TemplateView.as_view(template_name='index.html')),
]
# Add static serving configuration for development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
