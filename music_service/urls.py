from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from tracks import views as track_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("tracks/", include("tracks.urls")),  
    path("users/", include("users.urls")),
    path("", track_views.home, name="home"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)