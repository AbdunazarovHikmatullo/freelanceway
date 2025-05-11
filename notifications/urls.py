from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    # Страницы уведомлений
    path('', views.notification_list, name='notification_list'),
    path('<int:pk>/', views.notification_detail, name='notification_detail'),
    path('preferences/', views.notification_preferences, name='notification_preferences'),
    
    # Действия с уведомлениями
    path('<int:pk>/read/', views.mark_as_read, name='mark_as_read'),
    path('read-all/', views.mark_all_as_read, name='mark_all_as_read'),
    path('<int:pk>/delete/', views.delete_notification, name='delete_notification'),
    path('delete-all/', views.delete_all_notifications, name='delete_all_notifications'),
    
    # API для уведомлений
    path('api/unread/', views.get_unread_notifications, name='get_unread_notifications'),
    path('api/push/register/', views.register_push_device, name='register_push_device'),
    path('api/push/unregister/', views.unregister_push_device, name='unregister_push_device'),
]