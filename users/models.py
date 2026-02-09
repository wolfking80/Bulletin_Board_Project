from django.db import models
from django.contrib.auth.models import AbstractUser



class CustomUser(AbstractUser):
  email = models.EmailField(unique=True, null=True, blank=True)
  avatar = models.ImageField(upload_to="user_avatars/", null=True, blank=True)

  class Meta:
    verbose_name = 'Пользователь'
    verbose_name_plural = "Пользователи"
    db_table = "users"
