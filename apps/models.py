from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    class RoleStatus(models.TextChoices):
        USER = 'User', 'user'
        SUPERUSER = 'Superuser', 'superuser'

    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100)
    role = models.CharField(max_length=100, choices=RoleStatus.choices, default=RoleStatus.USER)
    email = models.EmailField(unique=True)
    created_at = models.DateField(auto_now_add=True)
    superuser_start_date = models.DateField(null=True, blank=True)
    superuser_end_date = models.DateField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.role == self.RoleStatus.SUPERUSER:
            if not self.superuser_start_date:
                self.superuser_start_date = timezone.now()
            if not self.superuser_end_date:
                self.superuser_end_date = timezone.now()
        else:
            self.superuser_start_date = None
            self.superuser_end_date = None
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username

class Warehouse(models.Model):
    location = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    user = models.ManyToManyField('User', related_name='warehouses')
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name
