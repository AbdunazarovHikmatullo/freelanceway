from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from vacancy.models import Vacancy
from freelancers.models import Freelancer

class VacancySitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9

    def items(self):
        return Vacancy.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.updated_at if hasattr(obj, 'updated_at') else obj.created_at

class FreelancerSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Freelancer.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.updated_at if hasattr(obj, 'updated_at') else obj.created_at

class StaticSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        return ['main:home', 'vacancy:list', 'freelancers:list']

    def location(self, item):
        return reverse(item)
