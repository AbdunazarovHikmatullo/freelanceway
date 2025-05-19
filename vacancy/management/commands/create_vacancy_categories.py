# vacancy/management/commands/create_vacancy_categories.py

from django.core.management.base import BaseCommand
from django.utils.text import slugify

from vacancy.models import Category

CATEGORIES = [
    ("Веб-разработка", "code"),
    ("Frontend", "web"),
    ("Backend", "memory"),
    ("Fullstack разработка", "layers"),
    ("Мобильная разработка iOS", "phone_iphone"),
    ("Мобильная разработка Android", "phone_android"),
    ("UI/UX дизайн", "design_services"),
    ("Графический дизайн", "brush"),
    ("3D моделирование", "three_d_rotation"),
    ("Анимация и motion graphics", "motion_photos_on"),
    ("Видео-монтаж", "movie"),
    ("Копирайтинг и контент", "edit"),
    ("SEO и маркетинг", "trending_up"),
    ("SMM и интернет-реклама", "share"),
    ("Email-маркетинг", "email"),
    ("Переводы и локализация", "translate"),
    ("Аналитика данных", "analytics"),
    ("Data Science / ML", "science"),
    ("AI / NLP", "smart_toy"),
    ("DevOps и CI/CD", "cloud_queue"),
    ("Системное администрирование", "settings_suggest"),
    ("Кибербезопасность", "security"),
    ("Blockchain / Crypto", "currency_bitcoin"),
    ("Game Development", "sports_esports"),
    ("QA / Тестирование", "bug_report"),
    ("Техническая документация", "description"),
    ("Виртуальная помощь", "support_agent"),
    ("CRM / ERP интеграции", "integration_instructions"),
]

class Command(BaseCommand):
    help = "Создаёт категории для приложения vacancy"

    def handle(self, *args, **options):
        for name, icon in CATEGORIES:
            slug = slugify(name)
            obj, created = Category.objects.get_or_create(
                slug=slug,
                defaults={"name": name, "icon": icon}
            )
            status = "Добавлена" if created else "Пропущена"
            self.stdout.write(f"[{status}] {name}")
