from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseRedirect
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.core.paginator import Paginator
from django.urls import reverse

from .models import Notification, NotificationType, NotificationPreference
from .services import NotificationService, PushNotificationService


@login_required
def notification_list(request):
    """Страница со списком уведомлений пользователя"""
    # Получаем все уведомления пользователя
    notifications_list = Notification.objects.filter(recipient=request.user).order_by('-created_at')
    
    # Пагинация
    paginator = Paginator(notifications_list, 20)  # 20 уведомлений на страницу
    page_number = request.GET.get('page')
    notifications = paginator.get_page(page_number)
    
    # Количество непрочитанных уведомлений
    unread_count = NotificationService.get_unread_count(request.user)
    
    return render(request, 'notifications/notification_list.html', {
        'notifications': notifications,
        'unread_count': unread_count,
    })


@login_required
def notification_detail(request, pk):
    """Страница с детальной информацией об уведомлении"""
    notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
    
    # Отмечаем уведомление как прочитанное
    if not notification.is_read:
        notification.mark_as_read()
    
    # Если есть URL для перехода, перенаправляем пользователя
    if notification.action_url:
        return HttpResponseRedirect(notification.action_url)
    
    return render(request, 'notifications/notification_detail.html', {
        'notification': notification,
    })


@login_required
@require_POST
def mark_as_read(request, pk):
    """Отмечает уведомление как прочитанное"""
    success = NotificationService.mark_as_read(pk, request.user)
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': success})
    
    if success:
        messages.success(request, 'Уведомление отмечено как прочитанное')
    else:
        messages.error(request, 'Не удалось отметить уведомление как прочитанное')
    
    return redirect('notifications:notification_list')


@login_required
@require_POST
def mark_all_as_read(request):
    """Отмечает все уведомления как прочитанные"""
    NotificationService.mark_all_as_read(request.user)
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    messages.success(request, 'Все уведомления отмечены как прочитанные')
    return redirect('notifications:notification_list')


@login_required
@require_POST
def delete_notification(request, pk):
    """Удаляет уведомление"""
    success = NotificationService.delete_notification(pk, request.user)
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': success})
    
    if success:
        messages.success(request, 'Уведомление удалено')
    else:
        messages.error(request, 'Не удалось удалить уведомление')
    
    return redirect('notifications:notification_list')


@login_required
@require_POST
def delete_all_notifications(request):
    """Удаляет все уведомления пользователя"""
    NotificationService.delete_all_notifications(request.user)
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    messages.success(request, 'Все уведомления удалены')
    return redirect('notifications:notification_list')


@login_required
def notification_preferences(request):
    """Страница с настройками уведомлений"""
    # Получаем все типы уведомлений
    notification_types = NotificationType.objects.all().order_by('name')
    
    # Получаем настройки пользователя
    user_preferences = NotificationPreference.objects.filter(user=request.user)
    
    # Создаем словарь с настройками для удобного доступа
    preferences_dict = {}
    for pref in user_preferences:
        preferences_dict[pref.notification_type_id] = pref
    
    if request.method == 'POST':
        # Обрабатываем форму с настройками
        for notification_type in notification_types:
            web_enabled = request.POST.get(f'web_{notification_type.id}') == 'on'
            email_enabled = request.POST.get(f'email_{notification_type.id}') == 'on'
            push_enabled = request.POST.get(f'push_{notification_type.id}') == 'on'
            
            NotificationService.update_preferences(
                request.user,
                notification_type.code,
                web_enabled=web_enabled,
                email_enabled=email_enabled,
                push_enabled=push_enabled
            )
        
        messages.success(request, 'Настройки уведомлений сохранены')
        return redirect('notifications:notification_preferences')
    
    return render(request, 'notifications/notification_preferences.html', {
        'notification_types': notification_types,
        'preferences_dict': preferences_dict,
    })


@login_required
def register_push_device(request):
    """Регистрирует устройство для push-уведомлений"""
    if request.method == 'POST':
        token = request.POST.get('token')
        device_type = request.POST.get('device_type', 'web')
        
        if token:
            PushNotificationService.register_device(request.user, token, device_type)
            return JsonResponse({'success': True})
    
    return JsonResponse({'success': False}, status=400)


@login_required
def unregister_push_device(request):
    """Отменяет регистрацию устройства"""
    if request.method == 'POST':
        token = request.POST.get('token')
        
        if token:
            PushNotificationService.unregister_device(request.user, token)
            return JsonResponse({'success': True})
    
    return JsonResponse({'success': False}, status=400)


@login_required
def get_unread_notifications(request):
    """API для получения непрочитанных уведомлений"""
    limit = int(request.GET.get('limit', 5))
    notifications = NotificationService.get_notifications(request.user, limit=limit)
    
    data = {
        'count': len(notifications),
        'total_unread': NotificationService.get_unread_count(request.user),
        'notifications': []
    }
    
    for notification in notifications:
        data['notifications'].append({
            'id': notification.id,
            'title': notification.title,
            'message': notification.message,
            'level': notification.level,
            'created_at': notification.created_at.strftime('%d.%m.%Y %H:%M'),
            'url': notification.get_absolute_url(),
        })
    
    return JsonResponse(data)