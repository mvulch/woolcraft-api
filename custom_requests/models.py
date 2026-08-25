from django.db import models
from django.conf import settings
# Create your models here.
class CustomRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Чакаща'
        REVIEWED = 'REVIEWED', 'Прегледана'
        ACCEPTED = 'ACCEPTED', 'Приета'
        REJECTED = 'REJECTED', 'Отказана'
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='custom_requests')
    title = models.CharField(max_length=100)
    description = models.TextField()
    specific_colors = models.CharField(max_length=80, blank=True)
    size = models.CharField(max_length=80)
    reference_image = models.ImageField(upload_to='custom_requests/',blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_finished = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Персонализирани заявки'
        verbose_name_plural = 'Персонализирани заявки'

    def __str__(self):
        return f'Заявка #{self.id} от {self.user.get_full_name()}'

class CustomRequestMessage(models.Model):
    request = models.ForeignKey(CustomRequest, on_delete=models.CASCADE, related_name='messages')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='custom_request_messages')
    text = models.CharField(max_length=400)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['created_at']
        verbose_name = 'Съобщение към заявка'
        verbose_name_plural = 'Съобщения към заявки'
    def __str__(self):
        role = 'член на екипа' if self.user.is_staff else 'клиент'
        return f'Отговор от {role} {self.user.get_full_name()} на заявка #{self.request.id} за парсонализирана изработка.'