from django.contrib.sitemaps import Sitemap
from vacancy.models import Vacancy

class VacancySitemap(Sitemap):
    changefreq = "daily"
    priority = 0.8

    def items(self):
        return Vacancy.objects.filter(status='open')

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return obj.get_absolute_url()
