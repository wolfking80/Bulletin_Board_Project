from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import Avg
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class CustomUser(AbstractUser):
    THEME_CHOICES = [("light", "Светлая"), ("dark", "Тёмная")]
    email = models.EmailField(unique=True, null=True, blank=True)
    phone_number = PhoneNumberField(
        null=True, blank=True, verbose_name="Номер телефона"
    )  # unique=True не нужно указывать
    phone_number_verified = models.BooleanField(
        default=False, verbose_name="Номер телефона подтверждён"
    )
    avatar = models.ImageField(upload_to="user_avatars/", null=True, blank=True)
    selected_theme = models.CharField(choices=THEME_CHOICES, default="dark")
    email_confirmed = models.BooleanField(default=False)
    notifications_enabled = models.BooleanField(
        default=False, verbose_name="Уведомления на Email"
    )

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        db_table = "users"

    @property
    def avatar_url(self):
        # Безопасный способ получить аватар
        if self.avatar and hasattr(self.avatar, "url"):
            return self.avatar.url
        return None

    @property
    def rating_data(self):
        # Расчет данных для отрисовки звездного рейтинга
        # Считаем среднее значение из связанных оценок (related_name='received_ratings' в SellerRating)
        avg = self.received_ratings.aggregate(Avg("score"))["score__avg"] or 0
        full = int(avg)
        half = 1 if (avg - full) >= 0.5 else 0
        return {
            "avg": round(avg, 1),
            "full": range(full),
            "half": range(half),
            "empty": range(5 - full - half),
            "total_count": self.received_ratings.count(),
        }


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ("favorite", "Добавление в избранное"),
        ("question", "Новый вопрос"),
        ("promotion", "Услуги продвижения"),
        ("moderation_success", "Модерация пройдена"),
        ("moderation_failed", "Модерация не пройдена"),
    ]

    recipient = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name="Получатель",
    )
    sender = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="sent_notifications",
        verbose_name="Отправитель",
        null=True,
        blank=True,
    )
    notification_type = models.CharField(
        max_length=30, choices=NOTIFICATION_TYPES, verbose_name="Тип уведомления"
    )
    message = models.CharField(max_length=255)

    # GenericForeignKey для привязки к любому объекту
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, null=True, blank=True
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey("content_type", "object_id")

    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Уведомление для {self.recipient.username} - {self.get_notification_type_display()}"
