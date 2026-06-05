from django.conf import settings
from django.db import models

# Create your models here.
class ChatSession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,null=False, related_name="chat_sessions")
    started_at = models.DateTimeField(auto_now_add=True)
    last_activity_at = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name = "chat session"
        verbose_name_plural = "chat sessions"
    def __str__(self):
        return f"Session {self.id} - {self.user.email}"

class ChatMessage(models.Model):
    chat_session = models.ForeignKey(ChatSession,on_delete=models.CASCADE, related_name="messages")
    text = models.TextField(blank=False)
    is_from_user = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        verbose_name = "chat message"
        verbose_name_plural = "chat messages"
    def __str__(self):
        sender = "Sender" if self.is_from_user else "Chat bot"
        return f"{sender}: {self.text[:20]}"