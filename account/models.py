from django.contrib.auth.models import AbstractUser
from django.core.validators import EmailValidator
from django.db import models


class UserProfile(AbstractUser):
    ROLE_CHOICES = [
        ('Admin', 'Admin'),
        ('Manager', 'Manager'),
        ('User', 'User'),
    ]

    email = models.EmailField(
        max_length=254,
        unique=True,
        validators=[EmailValidator(message="Please provide a valid email address.")]
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='User')
    is_active = models.BooleanField(default=False)

    @property
    def is_admin(self):
        return self.role == "Admin"

    @property
    def is_manager(self):
        return self.role == "Manager"

    @property
    def is_user(self):
        return self.role == "User"

    def __str__(self):
        return self.username


class EmailCode(models.Model):
    mail_code = models.CharField(max_length=4)
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="userprofile_codes")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.profile} - {self.mail_code}"
