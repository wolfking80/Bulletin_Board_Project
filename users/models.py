from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField



class CustomUser(AbstractUser):
  THEME_CHOICES = [
    ("light", "Светлая"),
    ("dark", "Тёмная")
  ]
  email = models.EmailField(unique=True, null=True, blank=True)
  phone_number = PhoneNumberField(null=True, blank=True, verbose_name='Номер телефона') # unique=True не нужно указывать
  phone_number_verified = models.BooleanField(default=False, verbose_name='Номер телефона подтверждён')
  avatar = models.ImageField(upload_to="user_avatars/", null=True, blank=True)
  selected_theme = models.CharField(choices=THEME_CHOICES, default="dark")
  email_confirmed = models.BooleanField(default=False)
  notifications_enabled = models.BooleanField(default=False, verbose_name="Уведомления на Email")

  class Meta:
    verbose_name = 'Пользователь'
    verbose_name_plural = "Пользователи"
    db_table = "users"
    
    
class Notification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    ad = models.ForeignKey('ads.Advertisement', on_delete=models.SET_NULL, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
