from django.contrib import admin
from .models import Category, Vacancy, Application


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'icon')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'client', 'budget_min', 'budget_max', 'status', 'created_at')
    list_filter = ('status', 'category', 'created_at')
    search_fields = ('title', 'description', 'required_skills')
    date_hierarchy = 'created_at'
    raw_id_fields = ('client',)


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('vacancy', 'freelancer', 'proposed_budget', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('vacancy__title', 'freelancer__user__username', 'cover_letter')
    date_hierarchy = 'created_at'
    raw_id_fields = ('vacancy', 'freelancer')