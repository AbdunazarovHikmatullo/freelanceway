from django.db import models
from django.utils import timezone
from django.urls import reverse
from users.models import User


class Category(models.Model):
    """Категория специализации фрилансера"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=50, help_text="Material icon name")
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Categories"


class Freelancer(models.Model):
    """Модель профиля фрилансера"""
    EXPERIENCE_CHOICES = (
        ('beginner', 'Начинающий (менее 1 года)'),
        ('intermediate', 'Средний (1-3 года)'),
        ('advanced', 'Опытный (3-5 лет)'),
        ('expert', 'Эксперт (более 5 лет)'),
    )
    
    AVAILABILITY_CHOICES = (
        ('full_time', 'Полная занятость'),
        ('part_time', 'Частичная занятость'),
        ('project_based', 'Проектная работа'),
        ('not_available', 'Временно не доступен'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='freelancer_profile')
    categories = models.ManyToManyField(Category, related_name='freelancers', blank=True)
    headline = models.CharField(max_length=100, blank=True, help_text="Краткое описание вашей специализации")
    bio = models.TextField(blank=True, help_text="Расскажите о себе и своем опыте")
    skills = models.CharField(max_length=255, blank=True, help_text="Перечислите ваши навыки через запятую")
    experience = models.CharField(max_length=20, choices=EXPERIENCE_CHOICES, default='beginner')
    hourly_rate = models.DecimalField(max_digits=8, decimal_places=2, default=0, help_text="Ваша часовая ставка в рублях")
    availability = models.CharField(max_length=20, choices=AVAILABILITY_CHOICES, default='full_time')
    
    telegram = models.CharField(max_length=50, blank=True)
    whatsapp = models.CharField(max_length=20, blank=True)
    
    # Портфолио и опыт
    portfolio_url = models.URLField(blank=True, help_text="Ссылка на ваше портфолио")
    education = models.TextField(blank=True, help_text="Информация о вашем образовании")
    certifications = models.TextField(blank=True, help_text="Информация о ваших сертификатах")
    
    # Рейтинг и статистика
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    reviews_count = models.PositiveIntegerField(default=0)
    completed_projects = models.PositiveIntegerField(default=0)
    phone_number = models.CharField(blank=True, null=True)
    # Дополнительные поля
    is_verified = models.BooleanField(default=False, help_text="Подтвержденный фрилансер")
    is_featured = models.BooleanField(default=False, help_text="Отображать в списке рекомендуемых")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - Фрилансер"
    
    def get_absolute_url(self):
        return reverse('freelancer_detail', args=[self.user.username])
    
    def get_skills_list(self):
        """Возвращает список навыков"""
        if not self.skills:
            return []
        return [skill.strip() for skill in self.skills.split(',')]
    
    def get_rating_display(self):
        """Возвращает рейтинг в виде звезд"""
        full_stars = int(self.rating)
        half_star = self.rating - full_stars >= 0.5
        empty_stars = 5 - full_stars - (1 if half_star else 0)
        
        stars = '★' * full_stars
        if half_star:
            stars += '½'
        stars += '☆' * empty_stars
        
        return stars
    
    class Meta:
        ordering = ['-rating', '-completed_projects']


class Portfolio(models.Model):
    """Модель для элементов портфолио фрилансера"""
    freelancer = models.ForeignKey(Freelancer, on_delete=models.CASCADE, related_name='portfolio_items')
    title = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='portfolio/', blank=True, null=True)
    project_url = models.URLField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.title} - {self.freelancer.user.username}"
    
    class Meta:
        ordering = ['-created_at']


class Review(models.Model):
    """Модель для отзывов о фрилансере"""
    freelancer = models.ForeignKey(Freelancer, on_delete=models.CASCADE, related_name='reviews')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='written_reviews')
    rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"Отзыв о {self.freelancer.user.username} от {self.author.username}"
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ('freelancer', 'author')