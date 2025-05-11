from django.contrib import admin
from .models import (
    NotificationType, NotificationPreference, Notification,
    EmailNotificationQueue, PushNotificationQueue, DeviceToken
)


@admin.register(NotificationType)
class NotificationTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'default_web', 'default_email', 'default_push')
    search_fields = ('name', 'code')
    list_filter = ('default_web', 'default_email', 'default_push')


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'notification_type', 'web_enabled', 'email_enabled', 'push_enabled')
    list_filter = ('web_enabled', 'email_enabled', 'push_enabled', 'notification_type')
    search_fields = ('user__username', 'user__email', 'notification_type__name')
    raw_id_fields = ('user',)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'notification_type', 'title', 'level', 'is_read', 'created_at')
    list_filter = ('level', 'is_read', 'is_sent_email', 'is_sent_push', 'notification_type', 'created_at')
    search_fields = ('recipient__username', 'recipient__email', 'title', 'message')
    raw_id_fields = ('recipient',)
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')


@admin.register(EmailNotificationQueue)
class EmailNotificationQueueAdmin(admin.ModelAdmin):
    list_display = ('notification', 'status', 'attempts', 'last_attempt', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('notification__recipient__username', 'notification__title')
    raw_id_fields = ('notification',)
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')


@admin.register(PushNotificationQueue)
class PushNotificationQueueAdmin(admin.ModelAdmin):
    list_display = ('notification', 'status', 'attempts', 'last_attempt', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('notification__recipient__username', 'notification__title')
    raw_id_fields = ('notification',)
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')


@admin.register(DeviceToken)
class DeviceTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'device_type', 'is_active', 'created_at', 'last_used_at')
    list_filter = ('device_type', 'is_active', 'created_at')
    search_fields = ('user__username', 'user__email', 'token')
    raw_id_fields = ('user',)
    date_hierarchy = 'created_at'