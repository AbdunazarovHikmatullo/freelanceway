from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

from .models import (
    Notification, NotificationType, NotificationPreference,
    EmailNotificationQueue, PushNotificationQueue, DeviceToken
)


class NotificationService:
    """Сервис для работы с уведомлениями"""
    
    @classmethod
    def create_notification(cls, recipient, notification_type_code, title, message, 
                           related_object=None, action_url='', level='info'):
        """
        Создает новое уведомление и ставит его в очередь для отправки
        
        Args:
            recipient: Пользователь, которому отправляется уведомление
            notification_type_code: Код типа уведомления
            title: Заголовок уведомления
            message: Текст уведомления
            related_object: Связанный объект (опционально)
            action_url: URL для перехода (опционально)
            level: Уровень важности (info, success, warning, error)
            
        Returns:
            Notification: Созданное уведомление
        """
        try:
            notification_type = NotificationType.objects.get(code=notification_type_code)
        except NotificationType.DoesNotExist:
            # Если тип уведомления не найден, создаем его с настройками по умолчанию
            notification_type = NotificationType.objects.create(
                code=notification_type_code,
                name=notification_type_code.replace('_', ' ').title(),
                default_web=True,
                default_email=True,
                default_push=False
            )
        
        # Создаем уведомление
        notification = Notification(
            recipient=recipient,
            notification_type=notification_type,
            title=title,
            message=message,
            level=level,
            action_url=action_url
        )
        
        # Если есть связанный объект, добавляем его
        if related_object:
            content_type = ContentType.objects.get_for_model(related_object)
            notification.content_type = content_type
            notification.object_id = related_object.pk
        
        notification.save()
        
        # Проверяем настройки пользователя для этого типа уведомлений
        try:
            preference = NotificationPreference.objects.get(
                user=recipient, 
                notification_type=notification_type
            )
            send_email = preference.email_enabled
            send_push = preference.push_enabled
        except NotificationPreference.DoesNotExist:
            # Если настройки не найдены, используем настройки по умолчанию
            send_email = notification_type.default_email
            send_push = notification_type.default_push
        
        # Добавляем в очередь email-уведомлений, если нужно
        if send_email:
            EmailNotificationQueue.objects.create(notification=notification)
        
        # Добавляем в очередь push-уведомлений, если нужно
        if send_push:
            PushNotificationQueue.objects.create(notification=notification)
        
        return notification
    
    @classmethod
    def mark_as_read(cls, notification_id, user):
        """Отмечает уведомление как прочитанное"""
        try:
            notification = Notification.objects.get(pk=notification_id, recipient=user)
            notification.mark_as_read()
            return True
        except Notification.DoesNotExist:
            return False
    
    @classmethod
    def mark_all_as_read(cls, user):
        """Отмечает все уведомления пользователя как прочитанные"""
        Notification.objects.filter(recipient=user, is_read=False).update(
            is_read=True, 
            updated_at=timezone.now()
        )
        return True
    
    @classmethod
    def get_unread_count(cls, user):
        """Возвращает количество непрочитанных уведомлений"""
        return Notification.objects.filter(recipient=user, is_read=False).count()
    
    @classmethod
    def get_notifications(cls, user, limit=None, include_read=False):
        """Возвращает уведомления пользователя"""
        query = Q(recipient=user)
        
        if not include_read:
            query &= Q(is_read=False)
        
        notifications = Notification.objects.filter(query).order_by('-created_at')
        
        if limit:
            notifications = notifications[:limit]
        
        return notifications
    
    @classmethod
    def delete_notification(cls, notification_id, user):
        """Удаляет уведомление"""
        try:
            notification = Notification.objects.get(pk=notification_id, recipient=user)
            notification.delete()
            return True
        except Notification.DoesNotExist:
            return False
    
    @classmethod
    def delete_all_notifications(cls, user):
        """Удаляет все уведомления пользователя"""
        Notification.objects.filter(recipient=user).delete()
        return True
    
    @classmethod
    def update_preferences(cls, user, notification_type_code, web_enabled=None, email_enabled=None, push_enabled=None):
        """Обновляет настройки уведомлений пользователя"""
        try:
            notification_type = NotificationType.objects.get(code=notification_type_code)
        except NotificationType.DoesNotExist:
            return False
        
        preference, created = NotificationPreference.objects.get_or_create(
            user=user,
            notification_type=notification_type,
            defaults={
                'web_enabled': notification_type.default_web,
                'email_enabled': notification_type.default_email,
                'push_enabled': notification_type.default_push
            }
        )
        
        # Обновляем только те поля, которые были переданы
        if web_enabled is not None:
            preference.web_enabled = web_enabled
        
        if email_enabled is not None:
            preference.email_enabled = email_enabled
        
        if push_enabled is not None:
            preference.push_enabled = push_enabled
        
        preference.save()
        return True


class EmailNotificationService:
    """Сервис для отправки email-уведомлений"""
    
    @classmethod
    def process_queue(cls, limit=50):
        """Обрабатывает очередь email-уведомлений"""
        queue_items = EmailNotificationQueue.objects.filter(
            status='pending'
        ).select_related('notification', 'notification__recipient')[:limit]
        
        for queue_item in queue_items:
            cls.send_email_notification(queue_item)
    
    @classmethod
    def send_email_notification(cls, queue_item):
        """Отправляет email-уведомление"""
        notification = queue_item.notification
        recipient = notification.recipient
        
        # Обновляем статус и счетчик попыток
        queue_item.status = 'sending'
        queue_item.attempts += 1
        queue_item.last_attempt = timezone.now()
        queue_item.save(update_fields=['status', 'attempts', 'last_attempt'])
        
        try:
            # Формируем контекст для шаблона
            context = {
                'notification': notification,
                'recipient': recipient,
                'site_name': settings.SITE_NAME,
                'site_url': settings.SITE_URL,
            }
            
            # Рендерим HTML и текстовую версии письма
            html_message = render_to_string('notifications/email/notification.html', context)
            text_message = render_to_string('notifications/email/notification.txt', context)
            
            # Отправляем письмо
            send_mail(
                subject=notification.title,
                message=text_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient.email],
                html_message=html_message,
                fail_silently=False
            )
            
            # Обновляем статус
            queue_item.status = 'sent'
            notification.is_sent_email = True
            notification.save(update_fields=['is_sent_email'])
            
        except Exception as e:
            # В случае ошибки обновляем статус и сохраняем сообщение об ошибке
            queue_item.status = 'failed'
            queue_item.error_message = str(e)
        
        queue_item.save()


class PushNotificationService:
    """Сервис для отправки push-уведомлений"""
    
    @classmethod
    def process_queue(cls, limit=50):
        """Обрабатывает очередь push-уведомлений"""
        queue_items = PushNotificationQueue.objects.filter(
            status='pending'
        ).select_related('notification', 'notification__recipient')[:limit]
        
        for queue_item in queue_items:
            cls.send_push_notification(queue_item)
    
    @classmethod
    def send_push_notification(cls, queue_item):
        """Отправляет push-уведомление"""
        notification = queue_item.notification
        recipient = notification.recipient
        
        # Обновляем статус и счетчик попыток
        queue_item.status = 'sending'
        queue_item.attempts += 1
        queue_item.last_attempt = timezone.now()
        queue_item.save(update_fields=['status', 'attempts', 'last_attempt'])
        
        try:
            # Получаем активные токены устройств пользователя
            device_tokens = DeviceToken.objects.filter(
                user=recipient,
                is_active=True
            )
            
            if not device_tokens.exists():
                # Если у пользователя нет активных устройств, отмечаем как отправленное
                queue_item.status = 'sent'
                notification.is_sent_push = True
                notification.save(update_fields=['is_sent_push'])
                queue_item.save(update_fields=['status'])
                return
            
            # Здесь должна быть логика отправки push-уведомлений через FCM, OneSignal или другой сервис
            # Для примера просто отмечаем как отправленное
            
            # Обновляем статус
            queue_item.status = 'sent'
            notification.is_sent_push = True
            notification.save(update_fields=['is_sent_push'])
            
        except Exception as e:
            # В случае ошибки обновляем статус и сохраняем сообщение об ошибке
            queue_item.status = 'failed'
            queue_item.error_message = str(e)
        
        queue_item.save()
    
    @classmethod
    def register_device(cls, user, token, device_type):
        """Регистрирует устройство для push-уведомлений"""
        device, created = DeviceToken.objects.update_or_create(
            user=user,
            token=token,
            defaults={
                'device_type': device_type,
                'is_active': True,
                'last_used_at': timezone.now()
            }
        )
        return device
    
    @classmethod
    def unregister_device(cls, user, token):
        """Отменяет регистрацию устройства"""
        try:
            device = DeviceToken.objects.get(user=user, token=token)
            device.is_active = False
            device.save(update_fields=['is_active'])
            return True
        except DeviceToken.DoesNotExist:
            return False