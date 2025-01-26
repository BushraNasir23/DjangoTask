from django.contrib import admin

# Register your models here.
from .models import UserProfile, EmailCode

admin.site.register(UserProfile)
admin.site.register(EmailCode)
