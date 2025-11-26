from django.db import models

# Create your models here.

class Advertisement(models.Model):
  title = models.CharField(max_length=200, verbose_name='Заголовок')
  text = models.TextField(verbose_name='Описание')
  goods_image = models.ImageField(
    upload_to='advertisements/',
    verbose_name='Изображение товара',
    blank=True,                         # Необязательно - разрешает пустое значение
    null=True                           # Необязательно - разрешает NULL в базе данных
)
  created_at = models.DateTimeField(auto_now_add=True)
  
  class Meta:
    verbose_name = 'объявление'
    verbose_name_plural = 'объявления'
    db_table = 'billboard'
  
  def __str__(self):
    return self.title