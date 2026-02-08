# backend/accounts/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True)
    last_password_change = models.DateTimeField(null=True, blank=True)
    capital = models.CharField(max_length=100, blank=True, verbose_name='Capital')
    city = models.CharField(max_length=100, blank=True)
    short_address = models.CharField(max_length=200, blank=True, verbose_name='Dirección corta')
    address = models.TextField(blank=True)
    country = models.CharField(max_length=100, blank=True, default='Venezuela')
    email_verified = models.BooleanField(default=False)
    
    def __str__(self):
        return self.user.email