# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    # Make email optional
    email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=32, unique=True)  # required for registration
    allowed_to_post = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['phone_number']  # Only phone_number is required for createsuperuser

    def __str__(self):
        return self.username
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'