from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    first_name = models.CharField(
        max_length=150, blank=True, verbose_name='First name')
    last_name = models.CharField(
        max_length=150, blank=True, verbose_name='Last name')
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=254, unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name', 'username']

    def __str__(self):
        return self.username

    class Meta:
        ordering = ['username']
