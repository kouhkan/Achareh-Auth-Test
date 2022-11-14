from django.db import models
from django.contrib.auth.models import AbstractBaseUser

from apps.accounts.managers import UserManager


class User(AbstractBaseUser):
    username = models.CharField(max_length=10, null=False, blank=False, unique=True, db_index=True)
    email = models.EmailField(max_length=150, null=True, blank=True, db_index=True)
    password = models.CharField(max_length=256, null=True, blank=True)
    first_name = models.CharField(max_length=64, null=True, blank=True)
    last_name = models.CharField(max_length=64, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_admin = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        unique_together = [('username', 'email'), ]

    def __str__(self):
        return f'{self.username}'
