from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', RedirectView.as_view(pattern_name='staff-dashboard', permanent=False)),
    path('admin/', admin.site.urls),
    path('events/', include('albums.urls')),
    path('', include('albums.urls')),
]

# 本機開發時提供媒體檔案
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=getattr(settings, 'MEDIA_ROOT', ''))
