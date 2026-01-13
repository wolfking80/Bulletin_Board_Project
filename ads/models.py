from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from unidecode import unidecode

User = get_user_model()


class Category(models.Model):
  name = models.CharField(max_length=100, verbose_name='Название')
  slug = models.SlugField(unique=True, editable=False, verbose_name="Слаг")
  image = models.ImageField(
        upload_to='categories/',
        blank=True,
        null=True,
        verbose_name='Изображение категории'
    )

  def save(self, *args, **kwargs):
    self.slug = slugify(unidecode(self.name))
    super().save(*args, **kwargs)

  def __str__(self):
    return self.name
  
  @property
  def ad_count(self):
    return self.ads.filter(status='published').count()  
  
  def get_absolute_url(self):
    return reverse('ads:category_ads', kwargs={'category_slug': self.slug})
  
  class Meta:
    verbose_name = 'Категория'
    verbose_name_plural = "Категории"
    db_table = "ads_categories"
    
    
class SubCategory(models.Model):
  name = models.CharField(max_length=100, verbose_name='Название')
  category = models.ForeignKey(Category,
    on_delete=models.CASCADE,
    related_name='subcategories',
    verbose_name="Категория"
    )
    
  def __str__(self):
    return f"{self.name} ({self.category.name})"
    
  class Meta:
    verbose_name = 'Подкатегория'
    verbose_name_plural = "Подкатегории"
    
    
class Tag(models.Model):
  name = models.CharField(max_length=100, verbose_name='Название')
  slug = models.SlugField(unique=True, editable=False, verbose_name='Тэг')

  def save(self, *args, **kwargs):
    self.slug = slugify(unidecode(self.name))
    super().save(*args, **kwargs)

  def __str__(self):
    return f'#{self.name}'
  
  def get_absolute_url(self):
    return reverse('ads:tag_ads', args=[self.slug])

  class Meta:
    verbose_name = 'Тег'
    verbose_name_plural = "Теги"
    db_table = "ad_tags"    
    
    
class Advertisement(models.Model):
  STATUS_CHOICES = (
    ('published', 'Опубликовано'),
    ('under_review', 'На проверке'),
    ('rejected', 'Отклонено')
  )
  title = models.CharField(max_length=200, blank=True, verbose_name='Заголовок')
  text = models.TextField(blank=True, verbose_name='Описание')
  slug = models.SlugField(max_length=200, unique=True, editable=False, verbose_name='Слаг')
  category = models.ForeignKey(Category,
    related_name='ads',
    on_delete=models.CASCADE,
    verbose_name="Категория"
  )
  subcategory = models.ForeignKey(
    SubCategory,
    on_delete=models.SET_NULL,  # Если удалить подкатегорию - у объявлений будет NULL
    null=True,                  # Может быть пустым
    blank=True,                 # Необязательное в форме
    verbose_name="Тип сделки"
    )
  tags = models.ManyToManyField(Tag, related_name='ads', blank=True, verbose_name='Теги')
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
  updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата последнего изменения")
  created_at = models.DateTimeField(auto_now_add=True)
  owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ads', verbose_name='Владелец')
  status = models.CharField(choices=STATUS_CHOICES, default='under_review', verbose_name="Статус")
  views = models.PositiveIntegerField(default=0, verbose_name="Просмотры")
  viewed_users = models.ManyToManyField(User, blank=True, related_name='viewed_ads', verbose_name="Просмотрено пользователями")
  
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
    
    
class Favorite(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
  ad = models.ForeignKey('Advertisement', on_delete=models.CASCADE, related_name='favorited_by')
    
  class Meta:
    unique_together = ['user', 'ad']  # один пользователь - одно избранное на объявление
    
  def __str__(self):
    return f"{self.user.username} ★ {self.ad.title}"