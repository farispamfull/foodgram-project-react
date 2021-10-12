from django.contrib.auth.models import AbstractUser
from django.db import models

from api import models as api_models


class User(AbstractUser):
    first_name = models.CharField(
        max_length=150, verbose_name='First name')
    last_name = models.CharField(
        max_length=150, verbose_name='Last name')
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=254, unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'username']

    def __str__(self):
        return self.username

    def is_subscribes(self, user):
        if not user.is_authenticated:
            return False
        if api_models.Follow.objects.select_related('author').filter(user=user,
                                                                     author=self).exists():
            return True
        return False

    def recipes_limit(self, limit):
        return self.recipes.all()[:int(limit)]

    @property
    def recipes_count(self):
        return self.recipes.count()

    class Meta:
        ordering = ['username']
