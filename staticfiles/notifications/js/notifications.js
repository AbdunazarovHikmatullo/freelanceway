/**
 * Скрипт для работы с уведомлениями
 */

document.addEventListener('DOMContentLoaded', function() {
    // Инициализация системы уведомлений
    const notificationSystem = {
        // Элементы DOM
        elements: {
            counter: document.getElementById('notification-counter'),
            dropdown: document.getElementById('notification-dropdown'),
            list: document.getElementById('notification-list'),
            markAllAsRead: document.getElementById('mark-all-as-read'),
            loadMore: document.getElementById('load-more-notifications')
        },
        
        // Состояние
        state: {
            unreadCount: 0,
            notifications: [],
            page: 1,
            hasMore: false,
            isLoading: false,
            isOpen: false
        },
        
        // Инициализация
        init: function() {
            this.loadNotifications();
            this.setupEventListeners();
            
            // Запускаем периодическую проверку новых уведомлений
            setInterval(() => this.checkNewNotifications(), 60000); // Каждую минуту
        },
        
        // Настройка обработчиков событий
        setupEventListeners: function() {
            // Открытие/закрытие выпадающего списка
            if (this.elements.counter) {
                this.elements.counter.addEventListener('click', (e) => {
                    e.preventDefault();
                    this.toggleDropdown();
                });
            }
            
            // Закрытие выпадающего списка при клике вне его
            document.addEventListener('click', (e) => {
                if (this.elements.dropdown && this.state.isOpen && !this.elements.dropdown.contains(e.target) && e.target !== this.elements.counter) {
                    this.closeDropdown();
                }
            });
            
            // Отметка всех уведомлений как прочитанных
            if (this.elements.markAllAsRead) {
                this.elements.markAllAsRead.addEventListener('click', (e) => {
                    e.preventDefault();
                    this.markAllAsRead();
                });
            }
            
            // Загрузка дополнительных уведомлений
            if (this.elements.loadMore) {
                this.elements.loadMore.addEventListener('click', (e) => {
                    e.preventDefault();
                    this.loadMoreNotifications();
                });
            }
        },
        
        // Загрузка уведомлений
        loadNotifications: function() {
            if (this.state.isLoading) return;
            
            this.state.isLoading = true;
            
            fetch('/notifications/api/unread/?limit=5')
                .then(response => response.json())
                .then(data => {
                    this.state.unreadCount = data.total_unread;
                    this.state.notifications = data.notifications;
                    this.state.hasMore = data.total_unread > data.notifications.length;
                    
                    this.updateCounter();
                    this.renderNotifications();
                })
                .catch(error => {
                    console.error('Ошибка при загрузке уведомлений:', error);
                })
                .finally(() => {
                    this.state.isLoading = false;
                });
        },
        
        // Проверка новых уведомлений
        checkNewNotifications: function() {
            fetch('/notifications/api/unread/?limit=1')
                .then(response => response.json())
                .then(data => {
                    if (data.total_unread !== this.state.unreadCount) {
                        this.state.unreadCount = data.total_unread;
                        this.updateCounter();
                        
                        // Если выпадающий список открыт, обновляем его содержимое
                        if (this.state.isOpen) {
                            this.loadNotifications();
                        }
                    }
                })
                .catch(error => {
                    console.error('Ошибка при проверке новых уведомлений:', error);
                });
        },
        
        // Загрузка дополнительных уведомлений
        loadMoreNotifications: function() {
            if (this.state.isLoading || !this.state.hasMore) return;
            
            this.state.page += 1;
            this.state.isLoading = true;
            
            fetch(`/notifications/api/unread/?limit=5&page=${this.state.page}`)
                .then(response => response.json())
                .then(data => {
                    this.state.notifications = [...this.state.notifications, ...data.notifications];
                    this.state.hasMore = data.total_unread > this.state.notifications.length;
                    
                    this.renderNotifications();
                })
                .catch(error => {
                    console.error('Ошибка при загрузке дополнительных уведомлений:', error);
                })
                .finally(() => {
                    this.state.isLoading = false;
                });
        },
        
        // Отметка всех уведомлений как прочитанных
        markAllAsRead: function() {
            fetch('/notifications/read-all/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCsrfToken(),
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        this.state.unreadCount = 0;
                        this.updateCounter();
                        
                        // Обновляем список уведомлений
                        this.loadNotifications();
                    }
                })
                .catch(error => {
                    console.error('Ошибка при отметке уведомлений как прочитанных:', error);
                });
        },
        
        // Отметка уведомления как прочитанного
        markAsRead: function(notificationId) {
            fetch(`/notifications/${notificationId}/read/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCsrfToken(),
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Уменьшаем счетчик непрочитанных уведомлений
                        this.state.unreadCount = Math.max(0, this.state.unreadCount - 1);
                        this.updateCounter();
                        
                        // Обновляем список уведомлений
                        this.loadNotifications();
                    }
                })
                .catch(error => {
                    console.error('Ошибка при отметке уведомления как прочитанного:', error);
                });
        },
        
        // Удаление уведомления
        deleteNotification: function(notificationId) {
            fetch(`/notifications/${notificationId}/delete/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCsrfToken(),
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Обновляем список уведомлений
                        this.loadNotifications();
                    }
                })
                .catch(error => {
                    console.error('Ошибка при удалении уведомления:', error);
                });
        },
        
        // Обновление счетчика непрочитанных уведомлений
        updateCounter: function() {
            if (this.elements.counter) {
                // Обновляем текст счетчика
                this.elements.counter.querySelector('.count').textContent = this.state.unreadCount;
                
                // Показываем или скрываем счетчик в зависимости от наличия непрочитанных уведомлений
                if (this.state.unreadCount > 0) {
                    this.elements.counter.classList.add('has-notifications');
                } else {
                    this.elements.counter.classList.remove('has-notifications');
                }
            }
        },
        
        // Отрисовка списка уведомлений
        renderNotifications: function() {
            if (!this.elements.list) return;
            
            // Очищаем список
            this.elements.list.innerHTML = '';
            
            if (this.state.notifications.length === 0) {
                // Если уведомлений нет, показываем соответствующее сообщение
                const emptyMessage = document.createElement('div');
                emptyMessage.className = 'empty-notifications';
                emptyMessage.innerHTML = `
                    <span class="material-symbols-outlined">notifications_off</span>
                    <p>У вас нет непрочитанных уведомлений</p>
                `;
                this.elements.list.appendChild(emptyMessage);
                
                // Скрываем кнопку "Загрузить еще"
                if (this.elements.loadMore) {
                    this.elements.loadMore.style.display = 'none';
                }
                
                return;
            }
            
            // Добавляем уведомления в список
            this.state.notifications.forEach(notification => {
                const notificationItem = document.createElement('div');
                notificationItem.className = `notification-item ${notification.level}`;
                notificationItem.innerHTML = `
                    <div class="notification-icon">
                        <span class="material-symbols-outlined">
                            ${this.getIconForLevel(notification.level)}
                        </span>
                    </div>
                    <div class="notification-content">
                        <h3 class="notification-title">${notification.title}</h3>
                        <div class="notification-message">${notification.message}</div>
                        <div class="notification-meta">
                            <span class="notification-time">${notification.created_at}</span>
                        </div>
                    </div>
                    <div class="notification-actions">
                        <a href="${notification.url}" class="notification-action" title="Просмотреть">
                            <span class="material-symbols-outlined">visibility</span>
                        </a>
                        <button class="notification-action mark-as-read" data-id="${notification.id}" title="Отметить как прочитанное">
                            <span class="material-symbols-outlined">mark_email_read</span>
                        </button>
                        <button class="notification-action delete-notification" data-id="${notification.id}" title="Удалить">
                            <span class="material-symbols-outlined">delete</span>
                        </button>
                    </div>
                `;
                
                // Добавляем обработчики событий для кнопок
                const markAsReadButton = notificationItem.querySelector('.mark-as-read');
                if (markAsReadButton) {
                    markAsReadButton.addEventListener('click', () => {
                        this.markAsRead(notification.id);
                    });
                }
                
                const deleteButton = notificationItem.querySelector('.delete-notification');
                if (deleteButton) {
                    deleteButton.addEventListener('click', () => {
                        this.deleteNotification(notification.id);
                    });
                }
                
                this.elements.list.appendChild(notificationItem);
            });
            
            // Показываем или скрываем кнопку "Загрузить еще"
            if (this.elements.loadMore) {
                this.elements.loadMore.style.display = this.state.hasMore ? 'block' : 'none';
            }
        },
        
        // Получение иконки для уровня уведомления
        getIconForLevel: function(level) {
            switch (level) {
                case 'info':
                    return 'info';
                case 'success':
                    return 'check_circle';
                case 'warning':
                    return 'warning';
                case 'error':
                    return 'error';
                default:
                    return 'notifications';
            }
        },
        
        // Открытие/закрытие выпадающего списка
        toggleDropdown: function() {
            if (!this.elements.dropdown) return;
            
            if (this.state.isOpen) {
                this.closeDropdown();
            } else {
                this.openDropdown();
            }
        },
        
        // Открытие выпадающего списка
        openDropdown: function() {
            if (!this.elements.dropdown) return;
            
            this.elements.dropdown.classList.add('open');
            this.state.isOpen = true;
            
            // Загружаем актуальные уведомления
            this.loadNotifications();
        },
        
        // Закрытие выпадающего списка
        closeDropdown: function() {
            if (!this.elements.dropdown) return;
            
            this.elements.dropdown.classList.remove('open');
            this.state.isOpen = false;
        },
        
        // Получение CSRF-токена
        getCsrfToken: function() {
            return document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';
        }
    };
    
    // Инициализация системы уведомлений
    notificationSystem.init();
    
    // Регистрация сервис-воркера для push-уведомлений
    if ('serviceWorker' in navigator && 'PushManager' in window) {
        navigator.serviceWorker.register('/static/notifications/js/service-worker.js')
            .then(function(registration) {
                console.log('ServiceWorker зарегистрирован успешно:', registration);
                
                // Запрашиваем разрешение на отправку push-уведомлений
                return registration.pushManager.getSubscription()
                    .then(function(subscription) {
                        if (subscription) {
                            return subscription;
                        }
                        
                        // Создаем новую подписку
                        return registration.pushManager.subscribe({
                            userVisibleOnly: true,
                            applicationServerKey: urlBase64ToUint8Array(
                                'YOUR_PUBLIC_VAPID_KEY_HERE' // Замените на ваш публичный VAPID-ключ
                            )
                        });
                    });
            })
            .then(function(subscription) {
                // Отправляем данные подписки на сервер
                return fetch('/notifications/api/push/register/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': notificationSystem.getCsrfToken()
                    },
                    body: JSON.stringify({
                        token: JSON.stringify(subscription),
                        device_type: 'web'
                    })
                });
            })
            .then(function(response) {
                if (!response.ok) {
                    throw new Error('Ошибка при регистрации устройства для push-уведомлений');
                }
                console.log('Устройство успешно зарегистрировано для push-уведомлений');
            })
            .catch(function(error) {
                console.error('Ошибка при регистрации для push-уведомлений:', error);
            });
    }
    
    // Вспомогательная функция для преобразования base64 в Uint8Array
    function urlBase64ToUint8Array(base64String) {
        const padding = '='.repeat((4 - base64String.length % 4) % 4);
        const base64 = (base64String + padding)
            .replace(/-/g, '+')
            .replace(/_/g, '/');
        
        const rawData = window.atob(base64);
        const outputArray = new Uint8Array(rawData.length);
        
        for (let i = 0; i < rawData.length; ++i) {
            outputArray[i] = rawData.charCodeAt(i);
        }
        return outputArray;
    }
});