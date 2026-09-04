from django.contrib import admin
from .models import CustomUser
from django.contrib.auth.admin import UserAdmin

def _superuser_only_admin(request):
    return request.user.is_active and request.user.is_superuser

admin.site.has_permission = _superuser_only_admin

# Register your models here.
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ("email", "first_name", "last_name", "username",
                    "date_joined", "last_login", "is_staff")
    search_fields = ("email", "username","first_name", "last_name")
    list_filter = ("is_active", "is_staff", "email_verified")
    readonly_fields = ("last_login", "date_joined")

    fieldsets = UserAdmin.fieldsets + (("Additional information",
                                        {"fields": ("phone", "email_verified")}),)

