from django.core.management.base import BaseCommand
from notifications.services import PushNotificationService

class Command(BaseCommand):
    help = 'Отправляет push-уведомления из очереди'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=50,
            help='Максимальное количество уведомлений для отправки за один запуск'
        )

    def handle(self, *args, **options):
        limit = options['limit']
        
        self.stdout.write(f'Отправка push-уведомлений (лимит: {limit})...')
        
        PushNotificationService.process_queue(limit=limit)
        
        self.stdout.write(self.style.SUCCESS('Отправка push-уведомлений завершена'))