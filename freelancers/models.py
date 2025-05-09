from django.db import models
from users.models import User



class Freelancer(models.Model):
    phone_number = models.CharField(max_length=15)
    telegram = models.CharField(max_length=255, blank=True, null=True),
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=700, blank=True, null=True)
    skills = models.CharField(max_length=255)
    experience = models.CharField(max_length=255)
    links = models.TextField(blank=True, null=True)
    raiting = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    def __str__(self):
        return self.user.username