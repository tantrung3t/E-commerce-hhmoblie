from django.db import models

# Create your models here.

class Token(models.Model):
    user_id = models.CharField(max_length=255)
    token_device = models.CharField(max_length=255)