from django import forms
from .models import Advertisement

class AdvertisementForm(forms.ModelForm):
    class Meta:
        model = Advertisement
        fields = ['title', 'text', 'price', 'contacts', 'goods_image']
        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'Название (максимум - 200 символов)'
            }),
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
            'text': 'Текст объявления',
            'price': 'Стоимость товара',
            'contacts': 'Контактный телефон',
            'goods_image': 'Изображение товара (необязательно)'
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