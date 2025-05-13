from django.db import models
from django.utils import timezone
from users.models import User
from freelancers.models import Freelancer


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=50, help_text="Material icon name")
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Categories"


class Vacancy(models.Model):
    STATUS_CHOICES = (
        ('open', 'Открыта'),
        ('in_progress', 'В работе'),
        ('completed', 'Завершена'),
        ('cancelled', 'Отменена'),
    )
    
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='vacancies')
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vacancies')
    budget_min = models.DecimalField(max_digits=10, decimal_places=2)
    budget_max = models.DecimalField(max_digits=10, decimal_places=2)
    deadline = models.DateField(null=True, blank=True)
    required_skills = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    views_count = models.IntegerField(default=0)
    applications_count = models.IntegerField(default=0)
    
    def __str__(self):
        return self.title
    
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('vacancy:vacancy_detail', args=[self.pk])
    
    class Meta:
        verbose_name_plural = "Vacancies"
        ordering = ['-created_at']


class Application(models.Model):
    STATUS_CHOICES = (
        ('pending', 'На рассмотрении'),
        ('accepted', 'Принята'),
        ('rejected', 'Отклонена'),
    )
    
    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE, related_name='applications')
    freelancer = models.ForeignKey(Freelancer, on_delete=models.CASCADE, related_name='applications')
    cover_letter = models.TextField()
    proposed_budget = models.DecimalField(max_digits=10, decimal_places=2)
    estimated_time = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"Заявка на {self.vacancy.title} от {self.freelancer.user.username}"
    
    class Meta:
        unique_together = ('vacancy', 'freelancer')