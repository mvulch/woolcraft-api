from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True,blank=False)
    phone = models.CharField(max_length=15, blank=True, null=True)
    email_verified = models.BooleanField(default=False)

    # so that auth system works with email not username
    USERNAME_FIELD = 'email'
    # fields that are asked for when creating superuser;
    # USERNAME_FIELD must not be included in REQUIRED_FIELDS as it is taken automatic
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        return self.email

