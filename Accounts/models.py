# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
import uuid
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
# models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class PasswordResetOTP(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    otp_hash = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    def is_expired(self):
        return timezone.now() > self.expires_at
class PasswordResetToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.expires_at