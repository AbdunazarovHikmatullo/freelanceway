from django.core.management.base import BaseCommand
from vacancy.models import Vacancy
from users.models import User
import random

class Command(BaseCommand):
    help = 'Создает 20 случайных вакансий'

    def handle(self, *args, **kwargs):
        # Получаем всех клиентов (пользователей, которые могут создавать вакансии)
        clients = User.objects.filter(is_client=True)

        if not clients.exists():
            self.stdout.write(self.style.ERROR('Нет клиентов для создания вакансий.'))
            return

        titles = [
            'Разработка веб-приложения',
            'Создание мобильного приложения',
            'Дизайн логотипа',
            'SEO-оптимизация сайта',
            'Разработка бэкенда',
            'Создание интернет-магазина',
            'Копирайтинг для блога',
            'Перевод текста',
            'Разработка игры',
            'Дизайн интерфейса',
            'Маркетинговая стратегия',
            'Анализ данных',
            'Техническая поддержка',
            'Создание анимации',
            'Разработка чат-бота',
            'Тестирование ПО',
            'Создание презентации',
            'Управление проектом',
            'Разработка API',
            'Обучение персонала'
        ]

        descriptions = [
            'Подробное описание задачи для выполнения.',
            'Требуется опыт работы в данной области.',
            'Срок выполнения — 2 недели.',
            'Бюджет обсуждается индивидуально.',
            'Ищем профессионала с опытом.',
            'Работа удаленная, график свободный.',
            'Необходимы примеры выполненных работ.',
            'Проект срочный, требуется начать немедленно.',
            'Долгосрочное сотрудничество приветствуется.',
            'Требуется соблюдение дедлайнов.'
        ]

        statuses = ['open', 'closed']

        for i in range(20):
            client = random.choice(clients)
            title = random.choice(titles)
            description = random.choice(descriptions)
            budget_min = random.randint(1000, 5000)
            budget_max = random.randint(6000, 20000)
            status = random.choice(statuses)

            Vacancy.objects.create(
                client=client,
                title=title,
                description=description,
                budget_min=budget_min,
                budget_max=budget_max,
                status=status
            )

        self.stdout.write(self.style.SUCCESS('Успешно создано 20 вакансий.'))