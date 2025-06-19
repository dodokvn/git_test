from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    list_display = ("id", "username", "email", "phone_number", "is_staff", "is_active")
    search_fields = ("username", "email", "phone_number")
    ordering = ("id",)
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Contact Info", {"fields": ("phone_number",)}),
    )
