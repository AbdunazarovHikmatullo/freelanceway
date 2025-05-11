from django.core.management.base import BaseCommand
from notifications.services import EmailNotificationService

class Command(BaseCommand):
    help = 'Отправляет email-уведомления из очереди'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=50,
            help='Максимальное количество уведомлений для отправки за один запуск'
        )

    def handle(self, *args, **options):
        limit = options['limit']
        
        self.stdout.write(f'Отправка email-уведомлений (лимит: {limit})...')
        
        EmailNotificationService.process_queue(limit=limit)
        
        self.stdout.write(self.style.SUCCESS('Отправка email-уведомлений завершена'))