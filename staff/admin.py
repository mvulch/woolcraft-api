from django.contrib import admin
from .models import Notification, NotificationRecipient

# Register your models here.
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("message", "type", "created_at")
    search_fields = ("message",)
    list_filter = ("type",)
    readonly_fields = ("created_at",)

@admin.register(NotificationRecipient)
class NotificationRecipientAdmin(admin.ModelAdmin):
    list_display = ("recipient__email", "notification__type", "is_read")
    search_fields = ("recipient__email",)
    list_filter = ("is_read", "notification__type",)
