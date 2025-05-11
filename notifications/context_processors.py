from .services import NotificationService

def notifications(request):
    """
    Контекстный процессор для добавления количества непрочитанных уведомлений
    в контекст шаблона
    """
    unread_count = 0
    
    if request.user.is_authenticated:
        unread_count = NotificationService.get_unread_count(request.user)
    
    return {
        'unread_notifications_count': unread_count
    }