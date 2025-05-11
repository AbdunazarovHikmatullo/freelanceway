from django.db import models
from django.conf import settings
from django.utils import timezone
from django.urls import reverse
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class NotificationType(models.Model):
    """Типы уведомлений в системе"""
    code = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Настройки по умолчанию для этого типа уведомлений
    default_web = models.BooleanField(default=True, help_text="Показывать на сайте по умолчанию")
    default_email = models.BooleanField(default=True, help_text="Отправлять по email по умолчанию")
    default_push = models.BooleanField(default=False, help_text="Отправлять push-уведомления по умолчанию")
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Тип уведомления"
        verbose_name_plural = "Типы уведомлений"


class NotificationPreference(models.Model):
    """Настройки уведомлений пользователя"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notification_preferences')
    notification_type = models.ForeignKey(NotificationType, on_delete=models.CASCADE)
    
    web_enabled = models.BooleanField(default=True, help_text="Показывать на сайте")
    email_enabled = models.BooleanField(default=True, help_text="Отправлять по email")
    push_enabled = models.BooleanField(default=False, help_text="Отправлять push-уведомления")
    
    class Meta:
        unique_together = ('user', 'notification_type')
        verbose_name = "Настройка уведомлений"
        verbose_name_plural = "Настройки уведомлений"


class Notification(models.Model):
    """Модель уведомления"""
    LEVELS = (
        ('info', 'Информация'),
        ('success', 'Успех'),
        ('warning', 'Предупреждение'),
        ('error', 'Ошибка'),
    )
    
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.ForeignKey(NotificationType, on_delete=models.CASCADE)
    
    title = models.CharField(max_length=255)
    message = models.TextField()
    level = models.CharField(max_length=20, choices=LEVELS, default='info')
    
    # Связь с любым объектом в системе (GenericForeignKey)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    related_object = GenericForeignKey('content_type', 'object_id')
    
    # URL для перехода при клике на уведомление
    action_url = models.CharField(max_length=255, blank=True)
    
    # Статус уведомления
    is_read = models.BooleanField(default=False)
    is_sent_email = models.BooleanField(default=False)
    is_sent_push = models.BooleanField(default=False)
    
    # Метаданные
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.notification_type} для {self.recipient.username}"
    
    def mark_as_read(self):
        """Отметить уведомление как прочитанное"""
        self.is_read = True
        self.save(update_fields=['is_read', 'updated_at'])
    
    def mark_as_unread(self):
        """Отметить уведомление как непрочитанное"""
        self.is_read = False
        self.save(update_fields=['is_read', 'updated_at'])
    
    def get_absolute_url(self):
        """Получить URL для перехода по уведомлению"""
        if self.action_url:
            return self.action_url
        return reverse('notifications:notification_detail', kwargs={'pk': self.pk})
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Уведомление"
        verbose_name_plural = "Уведомления"
        indexes = [
            models.Index(fields=['recipient', 'is_read', 'created_at']),
        ]


class EmailNotificationQueue(models.Model):
    """Очередь email-уведомлений для отправки"""
    notification = models.OneToOneField(Notification, on_delete=models.CASCADE, related_name='email_queue')
    
    # Статус отправки
    STATUS_CHOICES = (
        ('pending', 'В очереди'),
        ('sending', 'Отправляется'),
        ('sent', 'Отправлено'),
        ('failed', 'Ошибка'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Информация об отправке
    attempts = models.PositiveSmallIntegerField(default=0)
    last_attempt = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    
    # Метаданные
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Email для {self.notification.recipient.username}: {self.notification.title}"
    
    class Meta:
        ordering = ['created_at']
        verbose_name = "Очередь email-уведомлений"
        verbose_name_plural = "Очередь email-уведомлений"


class PushNotificationQueue(models.Model):
    """Очередь push-уведомлений для отправки"""
    notification = models.OneToOneField(Notification, on_delete=models.CASCADE, related_name='push_queue')
    
    # Статус отправки
    STATUS_CHOICES = (
        ('pending', 'В очереди'),
        ('sending', 'Отправляется'),
        ('sent', 'Отправлено'),
        ('failed', 'Ошибка'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Информация об отправке
    attempts = models.PositiveSmallIntegerField(default=0)
    last_attempt = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    
    # Метаданные
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Push для {self.notification.recipient.username}: {self.notification.title}"
    
    class Meta:
        ordering = ['created_at']
        verbose_name = "Очередь push-уведомлений"
        verbose_name_plural = "Очередь push-уведомлений"


class DeviceToken(models.Model):
    """Токены устройств для push-уведомлений"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='device_tokens')
    token = models.CharField(max_length=255)
    device_type = models.CharField(max_length=50, choices=(
        ('web', 'Веб-браузер'),
        ('android', 'Android'),
        ('ios', 'iOS'),
    ))
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    last_used_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.device_type}"
    
    class Meta:
        unique_together = ('user', 'token')
        verbose_name = "Токен устройства"
        verbose_name_plural = "Токены устройств"