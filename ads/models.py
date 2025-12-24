from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from unidecode import unidecode

User = get_user_model()

class Advertisement(models.Model):
  STATUS_CHOICES = (
    ('published', 'Опубликовано'),
    ('under_review', 'На проверке'),
    ('rejected', 'Отклонено')
  )
  title = models.CharField(max_length=200, blank=True, verbose_name='Заголовок')
  text = models.TextField(blank=True, verbose_name='Описание')
  slug = models.SlugField(max_length=200, unique=True, editable=False, verbose_name='Слаг')
  category = models.ForeignKey(
    'Category',
    related_name='ads',
    on_delete=models.CASCADE,
    verbose_name="Категория"
  )
  goods_image = models.ImageField(
    upload_to='advertisements/',
    verbose_name='Изображение товара',
    blank=True,                         # Необязательно - разрешает пустое значение
    null=True                           # Необязательно - разрешает NULL в базе данных
)
  price = models.DecimalField(
    max_digits=10, 
    decimal_places=2,
    verbose_name='Цена товара',
    blank=True,
    null=True                        # если цена может быть не указана
)
  contacts = PhoneNumberField(
    ("Контактный телефон"),
    blank=True,
    help_text="В формате +7XXXXXXXXXX"
)
  created_at = models.DateTimeField(auto_now_add=True)
  owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ads', verbose_name='Владелец')
  status = models.CharField(choices=STATUS_CHOICES, default='under_review', verbose_name="Статус")
  
  class Meta:
    verbose_name = 'объявление'
    verbose_name_plural = 'объявления'
    db_table = 'billboard'
  
  def __str__(self):
    return self.title
  
  def save(self, *args, **kwargs):
    super().save(*args, **kwargs)
    self.slug = f"{slugify(unidecode(self.title))}-{self.pk}"
    super().save(*args, **kwargs)
    
    
class Category(models.Model):
  name = models.CharField(max_length=100, verbose_name='Название')
  slug = models.SlugField(unique=True, editable=False, verbose_name="Слаг")

  def save(self, *args, **kwargs):
    self.slug = slugify(unidecode(self.name))
    super().save(*args, **kwargs)

  def __str__(self):
    return self.name
  
  def get_absolute_url(self):
    return reverse('ads:ads_category', kwargs={'category_slug': self.slug})
  
  class Meta:
    verbose_name = 'Категория'
    verbose_name_plural = "Категории"
    db_table = "ads_categories"    