from django.db import models
from django.db.models import Q, Avg, Count, F
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from unidecode import unidecode
from phonenumber_field.modelfields import PhoneNumberField

User = get_user_model()

class CategoryQuerySet(models.QuerySet):
  def with_ad_count(self):
    """Оптимизированный подсчет объявлений (базовый пример)"""
    return self.annotate(ann_ad_count=models.Count('ads', filter=models.Q(ads__status='published')))


class Category(models.Model):
  name = models.CharField(max_length=100, verbose_name='Название')
  slug = models.SlugField(editable=False, verbose_name="Слаг")
  image = models.ImageField(
        upload_to='categories/',
        blank=True,
        null=True,
        verbose_name='Изображение категории'
    )
  parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='children', 
        verbose_name="Родительская категория"
    )
  
  objects = CategoryQuerySet.as_manager()
  
  class Meta:
    verbose_name = 'Категория'
    verbose_name_plural = "Категории"
    db_table = "ads_categories"
    
    
  @property
  def total_ads_count(self):
    from ads.models import Advertisement
    return Advertisement.objects.filter(
        category__slug__startswith=self.slug, 
        status='published'
    ).count()
    

  def save(self, *args, **kwargs):
    if not self.slug:
      base_slug = slugify(unidecode(self.name))
      # Если есть родитель, добавляем его слаг для уникальности URL пути
      self.slug = f"{self.parent.slug}-{base_slug}" if self.parent else base_slug
    super().save(*args, **kwargs)

  def __str__(self):
    return self.name

  def get_absolute_url(self):
    return reverse('ads:category_ads', kwargs={'category_slug': self.slug})
  
    
class Tag(models.Model):
  name = models.CharField(unique=True, max_length=100, verbose_name='Название')
  slug = models.SlugField(unique=True, editable=False, verbose_name='Тэг')

  def save(self, *args, **kwargs):
    # Приводим к нижнему регистру, чтобы "Авто" и "авто" были одним тегом
    self.name = self.name.lower().strip()
    if not self.slug:
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
    
# Создаем новый классб наследуем от стандартного models.QuerySet
# Это позволяет добавлять свои методы фильтрации (например, .with_metrics()) 
# прямо в цепочки запросов базы данных
class AdvertisementQuerySet(models.QuerySet):
  def with_metrics(self):
    """Оптимизированный расчет рейтинга (среднее 1-5) и лайков"""
    return self.annotate(
        fav_count=Count('favorited_by', distinct=True),
        # Просто берем среднее арифметическое оценок продавца
        seller_rating=Avg('owner__received_ratings__score')
      )

# Метод для текстового поиска. Принимает поисковую строку и два флага для расширения зоны поиска
  def search(self, query_text, search_category=False, search_tag=False):
# Если строка поиска пустая, метод мгновенно возвращает текущий QuerySet без изменений   
    if not query_text:
        return self
      
    # Базовый поиск по названию и тексту
    q_objects = Q(title__icontains=query_text) | Q(text__icontains=query_text)
    
    if search_category:
        # Находим категории, которые подходят под искомый запрос
        found_categories = Category.objects.filter(name__icontains=query_text)
        
        # Для каждой найденной категории ищем все объявления, 
        # слаг которых начинается со слага этой категории (включая детей)
        for cat in found_categories:
            q_objects |= Q(category__slug__startswith=cat.slug)
            
    if search_tag:
        q_objects |= Q(tags__name__icontains=query_text)
    # .distinct() удаляет дубликаты объявлений из результата 
    # (могут возникнуть из-за связей "многие-ко-многим")    
    return self.filter(q_objects).distinct()

  def apply_filters(self, min_price=None, max_price=None, min_rating=None):
    # Локальная переменная для постепенного накопления фильтров
    qs = self
    if min_price:
        qs = qs.filter(price__gte=min_price)
    if max_price:
        qs = qs.filter(price__lte=max_price)
    if min_rating:
        # Теперь просто сравниваем: 4.5 >= 4.0
        qs = qs.filter(seller_rating__gte=float(min_rating))
    return qs

#  Метод "умной" сортировки. Логика зависит от того, 
# пришел ли пользователь из поиска (is_search=True) или просто смотрит каталог
  def smart_order(self, is_search=False):
    if is_search:
      ordering = [
        '-promotion__is_top', 
        F('price').asc(nulls_last=True), 
        F('seller_rating').desc(nulls_last=True)
        ]
    else:
      ordering = ['-promotion__is_top', '-promotion__is_vip', '-promotion__is_urgent']
    return self.order_by(*ordering, '-created_at', '-id').distinct()    
    
    
class Advertisement(models.Model):
  STATUS_CHOICES = (
    ('published', 'Опубликовано'),
    ('under_review', 'На проверке'),
    ('rejected', 'Отклонено')
  )
  title = models.CharField(max_length=200, blank=True, verbose_name='Заголовок')
  text = models.TextField(blank=True, verbose_name='Описание')
  slug = models.SlugField(max_length=255, unique=True, editable=False, verbose_name='Слаг')
  category = models.ForeignKey(Category,
    related_name='ads',
    on_delete=models.PROTECT,
    verbose_name="Категория"
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
    db_index=True,
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
  status = models.CharField(choices=STATUS_CHOICES, default='under_review', db_index=True, verbose_name="Статус")
  views = models.PositiveIntegerField(default=0, verbose_name="Просмотры")
  viewed_users = models.ManyToManyField(User, blank=True, related_name='viewed_ads', verbose_name="Просмотрено пользователями")
  
  # связываем кастомный QuerySet с моделью Django в качестве главного менеджера базы данных
  # это позволяет: 
  # Доступ к методам через objects
  # Создание цепочек методов (Chaining), например 
  # Advertisement.objects.with_metrics().apply_filters(min_price=1000).smart_order(is_search=True)
  # Исключение дублирования кода
  objects = AdvertisementQuerySet.as_manager()
  
  class Meta:
    verbose_name = 'объявление'
    verbose_name_plural = 'объявления'
    db_table = 'billboard'
  
  def __str__(self):
    return self.title
  
  def save(self, *args, **kwargs):
    if not self.slug:
    # Используем временный уникальный маркер (timestamp или uuid), 
    # чтобы избежать двойного save()
      import time
      temp_slug = slugify(unidecode(self.title))
      self.slug = f"{temp_slug}-{int(time.time())}"
    super().save(*args, **kwargs)
    
    
class AdPromotion(models.Model):
  # Связь с основным объявлением
  ad = models.OneToOneField(
    Advertisement, 
    on_delete=models.CASCADE, 
    related_name='promotion',
    verbose_name="Объявление"
  )
    
  # Визуальные фишки
  is_vip = models.BooleanField(default=False, verbose_name="VIP статус (значок)")
  is_urgent = models.BooleanField(default=False, verbose_name="Срочно (огонек)")
  is_colored = models.BooleanField(default=False, verbose_name="Выделение цветом (рамка)")
  is_top = models.BooleanField(default=False, verbose_name="Поднято в топ")

  # для проверки оплаты
  # (True становится только после успешного ответа от платежки)
  vip_paid = models.BooleanField(default=False, verbose_name="VIP оплачен")
  top_paid = models.BooleanField(default=False, verbose_name="Топ оплачен")
  urgent_paid = models.BooleanField(default=False, verbose_name="Топ оплачен")
  colored_paid = models.BooleanField(default=False, verbose_name="Рамка оплачена")

  class Meta:
    verbose_name = 'Продвижение объявления'
    verbose_name_plural = 'Продвижение объявлений'

  def __str__(self):
    return f"Промо для: {self.ad.title}"
    
    
class Favorite(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
  ad = models.ForeignKey('Advertisement', on_delete=models.CASCADE, related_name='favorited_by')
    
  class Meta:
    unique_together = ['user', 'ad']  # один пользователь - одно избранное на объявление
    
  def __str__(self):
    return f"{self.user.username} ★ {self.ad.title}"
  
  
class SellerRating(models.Model):
    voter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_ratings')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_ratings')
    score = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])

    class Meta:
        unique_together = ['voter', 'seller'] # Один юзер — один голос за одного продавца
        
        
class AdQuestion(models.Model):
  # Связь с объявлением: одно объявление — много вопросов
  ad = models.ForeignKey(Advertisement, on_delete=models.CASCADE, related_name='questions')
  # Связь с автором вопроса: один юзер — много вопросов
  author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ad_questions')
  # Ссылка на саму себя для ответов
  parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name="replies")
  text = models.TextField(verbose_name="Текст вопроса")
  created_at = models.DateTimeField(auto_now_add=True)

  class Meta:
    ordering = ['-created_at'] # Сначала новые вопросы
    verbose_name = 'Вопрос по товару'
    verbose_name_plural = 'Вопросы по товарам'

  def __str__(self):
    if self.parent:
      return f'Ответ от {self.author} для {self.parent.author}'
    return f'Вопрос от {self.author} к "{self.ad.title}"'          