from django.db import models

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.text import slugify
from unidecode import unidecode
from ads.models import Advertisement
from phonenumber_field.modelfields import PhoneNumberField

User = get_user_model()

class Type(models.Model):
    name = models.CharField(max_length=200, unique=True, verbose_name='Название')
    slug = models.SlugField(unique=True, editable=False, verbose_name='Слаг')
    services = models.ManyToManyField('Service', related_name='types', verbose_name='Услуги')

    class Meta:
        verbose_name = "Тип услуги"
        verbose_name_plural = "Типы услуг"
        db_table = "paid_service_types"

    def save(self, *args, **kwargs):
        # метод генерации слагов
        self.name = self.name.strip()
        self.slug = slugify(unidecode(self.name))
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Service(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название')
    description = models.TextField(verbose_name='Описание')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    duration = models.DurationField(verbose_name='Срок действия')
    can_be_combined = models.BooleanField(default=True, verbose_name='Можно комбинировать с другими услугами')
    is_exclusive = models.BooleanField(
        default=False, 
        verbose_name='Эксклюзивная услуга', 
        help_text='Может быть активна только на одном объявлении во всей системе в один момент времени'
    )

    class Meta:
        verbose_name = "Услуга"
        verbose_name_plural = "Услуги"
        db_table = "promo"

    def __str__(self):
        return self.name


class Request(models.Model):
    STATUS_CHOICES = [
        ('unread', 'Не прочитано'),
        ('pending', 'В ожидании'),
        ('cancelled', 'Отменено'),
        ('completed', 'Выполнено')
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    phone = PhoneNumberField(region="RU", verbose_name='Телефон')
    comment = models.TextField(blank=True, null=True, verbose_name='Комментарий')
    status = models.CharField(max_length=9, choices=STATUS_CHOICES, default='unread', verbose_name='Статус')
    type = models.ForeignKey(Type, on_delete=models.CASCADE, verbose_name='Тип')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, verbose_name='Услуга')
    
    # Связь с Доской Объявлений: к какому объявлению применяется платная услуга
    ad = models.ForeignKey(Advertisement, on_delete=models.CASCADE, related_name='service_requests', verbose_name='Объявление', null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    def __str__(self):
        return f'{self.user.username} - {self.phone} ({self.service.name})'

    class Meta:
        verbose_name = "Обращение"
        verbose_name_plural = "Обращения"
        db_table = "paid_service_requests"


class Review(models.Model):
    STATUS_CHOICES = [
        ('rejected', 'отклонён'),
        ('published', 'опубликован')
    ]
    RATING_CHOICES = [
        (1, '1 звезда'),
        (2, '2 звезды'),
        (3, '3 звезды'),
        (4, '4 звезды'),
        (5, '5 звезд')
    ]
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='service_reviews', verbose_name='Автор')
    text = models.TextField(verbose_name='Текст')
    rating = models.IntegerField(choices=RATING_CHOICES, verbose_name='Оценка')
    status = models.CharField(max_length=9, choices=STATUS_CHOICES, default='published', verbose_name='Статус')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='reviews', verbose_name='Услуга')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    def __str__(self):
        return f'Отзыв от {self.author.username} - Оценка: {self.rating}'

    class Meta:
        verbose_name = "Отзыв об услуге"
        verbose_name_plural = "Отзывы об услугах"
        constraints = [
            models.UniqueConstraint(fields=['author', 'service'], name='unique_user_service_review')
        ]
        db_table = "paid_service_reviews"


class Purchase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchases', verbose_name='Пользователь')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='purchases', verbose_name='Услуга')
    ad = models.ForeignKey(Advertisement, on_delete=models.SET_NULL, related_name='active_services', verbose_name='Продвигаемое объявление', null=True, blank=True)
    ever_used = models.BooleanField(default=False, verbose_name='Хоть раз была использована')
    is_available = models.BooleanField(default=True, verbose_name='В наличии')

    class Meta:
        verbose_name = "Покупка"
        verbose_name_plural = "Покупки"
        db_table = "paid_service_purchases"
        constraints = [
            models.UniqueConstraint(fields=['user', 'service'], name='unique_user_service_purchase')
        ]

    def __str__(self):
        return f"{self.user.username} - {self.service.name}"


import promo.signals
