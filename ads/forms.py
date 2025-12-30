from django import forms
from .models import Advertisement

class AdvertisementForm(forms.ModelForm):
    tags_input = forms.CharField(
    required=False,
    widget=forms.TextInput(attrs={
      'class': 'form-control',
      'placeholder': 'Введите теги через запятую...'
    }),
    label="Теги"
  )
    class Meta:
        model = Advertisement
        fields = ['title', 'category', 'subcategory', 'text', 'price', 'contacts', 'goods_image']
        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'Название (максимум - 200 символов)'
            }),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'subcategory': forms.Select(attrs={'class': 'form-select'}),
            'text': forms.Textarea(attrs={
                'rows': 5,
                'placeholder': 'Подробное описание товара...'
            }),
            'price': forms.NumberInput(attrs={
                'min': 0,
                'step': 0.01,
                'placeholder': '0.00'
            }),
            'contacts': forms.TextInput(attrs={
                'placeholder': '+7 (XXX) XXX-XX-XX'
            }),
            'goods_image': forms.ClearableFileInput(attrs={
                'accept': 'image/*'
            })
        }
        labels = {
            'title': 'Заголовок объявления',
            'category': 'Категория:',
            'text': 'Текст объявления',
            'price': 'Стоимость товара',
            'contacts': 'Контактный телефон',
            'goods_image': 'Изображение товара (необязательно)'
        }
        help_texts = {
      'category': " Выберите категорию для своего объявления..."
    }
    
    
    def clean_title(self):
      text = self.cleaned_data['title'].strip()
      if not text:
        raise forms.ValidationError("Заголовок обязателен!")
      return text


    def clean_text(self):
      text = self.cleaned_data['text'].strip()
      if not text:
        raise forms.ValidationError("Текст обязателен!")
      return text


    def clean_contacts(self):
      contacts = self.cleaned_data['contacts']
    
      if not contacts:
        raise forms.ValidationError("Контактный телефон обязателен!")

      if not contacts.is_valid():
        raise forms.ValidationError("Недействительный номер телефона!")
      return contacts


    def clean_price(self):
      price = self.cleaned_data['price']
      if price is not None and price < 0:
        raise forms.ValidationError("Цена не может быть отрицательной!")
      return price
    
    
    def clean_tags_input(self):
      """
      Разбивает строку на список тегов:
      - удаляет лишние пробелы вокруг
      - приводит к нижнему регистру
      """
      tags_str = self.cleaned_data.get('tags_input')
      tags = [tag.strip().lower() for tag in tags_str.split(',') if tag.strip()]
      return tags