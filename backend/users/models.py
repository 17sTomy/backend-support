from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

# Create your models here.

class User(AbstractUser): 
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    username = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    avatar = models.ImageField(default='user.png')
    date_joined = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        if not self.pk:  # Si el usuario es nuevo, cifrar la contraseña
            self.set_password(self.password)
        super(User, self).save(*args, **kwargs)