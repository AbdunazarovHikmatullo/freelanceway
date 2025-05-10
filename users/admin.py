from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_freelancer', 'is_client', 'is_staff')
    list_filter = ('is_freelancer', 'is_client', 'is_staff', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Персональная информация', {'fields': ('first_name', 'last_name', 'email', 'avatar', 'bio', 'location')}),
        ('Социальные сети', {'fields': ('website', 'github', 'twitter', 'linkedin')}),
        ('Тип пользователя', {'fields': ('is_freelancer', 'is_client')}),
        ('Настройки', {'fields': ('email_notifications',)}),
        ('Права доступа', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Важные даты', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_freelancer', 'is_client'),
        }),
    )