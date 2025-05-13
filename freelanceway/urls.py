from django.contrib import admin
from django.urls import path , include
from django.conf import settings
from django.conf.urls.static import static
from sitemaps import VacancySitemap
from django.contrib.sitemaps.views import sitemap
sitemaps = {
    'vacancies': VacancySitemap,
}


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('users/', include('users.urls')),
    path('freelancers/', include('freelancers.urls')),
    path('vacancy/', include('vacancy.urls')),
    path('notifications/', include('notifications.urls', namespace='notifications')),


    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
