from django.contrib import admin
from .models import Freelancer, Portfolio, Review, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'icon')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(Freelancer)
class FreelancerAdmin(admin.ModelAdmin):
    list_display = ('user', 'headline', 'experience', 'hourly_rate', 'rating', 'is_verified', 'is_featured')
    list_filter = ('experience', 'availability', 'is_verified', 'is_featured', 'created_at')
    search_fields = ('user__username', 'user__email', 'headline', 'skills')
    raw_id_fields = ('user',)
    filter_horizontal = ('categories',)
    readonly_fields = ('rating', 'reviews_count', 'completed_projects', 'created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('user', 'headline', 'bio', 'categories', 'skills')
        }),
        ('Опыт и ставка', {
            'fields': ('experience', 'hourly_rate', 'availability')
        }),
        ('Портфолио и образование', {
            'fields': ('portfolio_url', 'education', 'certifications')
        }),
        ('Статистика', {
            'fields': ('rating', 'reviews_count', 'completed_projects')
        }),
        ('Статус', {
            'fields': ('is_verified', 'is_featured')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ('title', 'freelancer', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('title', 'description', 'freelancer__user__username')
    raw_id_fields = ('freelancer',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('freelancer', 'author', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('freelancer__user__username', 'author__username', 'comment')
    raw_id_fields = ('freelancer', 'author')