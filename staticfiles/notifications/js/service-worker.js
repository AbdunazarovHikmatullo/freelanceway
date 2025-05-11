/**
 * Сервис-воркер для обработки push-уведомлений
 */

self.addEventListener('push', function(event) {
    if (event.data) {
        const data = event.data.json();
        
        // Показываем уведомление
        event.waitUntil(
            self.registration.showNotification(data.title, {
                body: data.message,
                icon: '/static/base/img/logo.svg',
                badge: '/static/notifications/img/badge.png',
                tag: data.id,
                data: {
                    url: data.url
                },
                actions: [
                    {
                        action: 'view',
                        title: 'Просмотреть'
                    },
                    {
                        action: 'close',
                        title: 'Закрыть'
                    }
                ]
            })
        );
    }
});

// Обработка клика по уведомлению
self.addEventListener('notificationclick', function(event) {
    event.notification.close();
    
    if (event.action === 'view' || event.action === '') {
        // Открываем URL из уведомления
        event.waitUntil(
            clients.openWindow(event.notification.data.url)
        );
    }
});