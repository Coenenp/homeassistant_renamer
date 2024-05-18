from django.db import models
from django.contrib.auth.models import User

class AppConfig(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    host = models.CharField(max_length=100)
    tls_enabled = models.BooleanField(default=False)
    access_token = models.CharField(max_length=255)

    def __str__(self):
        return self.host
