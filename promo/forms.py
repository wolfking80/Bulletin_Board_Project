import re
from django import forms

from ads.models import Advertisement
from .models import Request, Review, Service, Type
from phonenumber_field.formfields import PhoneNumberField

class PaidServiceRequestForm(forms.ModelForm):
    phone = PhoneNumberField(
        region="RU",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+7 (XXX) XXX-XX-XX'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # если форма содержит ошибки, добавляем класс 'is-invalid'
        for field_name, field in self.fields.items():
            if self.errors.get(field_name):
                widget_classes = field.widget.attrs.get('class', '')
                field.widget.attrs['class'] = f'{widget_classes} is-invalid'.strip()

    class Meta:
        model = Request
        # Выводим все 5 полей, включая тип и услугу
        fields = ["ad", "type", "service", "phone", "comment"]
        widgets = {
            # Делаем все три поля чистыми выпадающими списками Select
            "ad": forms.Select(attrs={"class": "form-select"}),
            "type": forms.Select(attrs={"class": "form-select"}),
            "service": forms.Select(attrs={"class": "form-select"}),
            "comment": forms.Textarea(attrs={
                "class": "form-control", 
                "rows": 4, 
                "placeholder": "Ваш комментарий к заявке"
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        service_type = cleaned_data.get("type")
        service = cleaned_data.get("service")

        # проверяем, что выбранная услуга входит в выбранный пакет
        if service_type and service:
            type_services = set(service_type.services.values_list("name", flat=True).distinct())
            type_services = {s.lower() for s in type_services}
            current_service_name = service.name.lower()
            
            if current_service_name not in type_services:
                self.add_error(
                    "service", 
                    f"Услуга '{service.name}' не относится к пакету '{service_type.name}'."
                )
        return cleaned_data


class PaidServiceReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["text", "rating"]
        widgets = {
            "text": forms.Textarea(attrs={
                "class": "form-control", 
                "rows": 4, 
                "placeholder": "Оставьте ваш отзыв о работе услуги...",
            }),
            "rating": forms.RadioSelect(choices=[(i, f"{i} Звезд") for i in range(1, 6)]),
        }
        
        
class PaymentOrderForm(forms.Form):
    """Форма для создания заказа на оплату"""
    
    ad = forms.ModelChoiceField(
        queryset=Advertisement.objects.none(),
        label="Объявление",
        help_text="Выберите объявление, которое хотите продвинуть",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    comment = forms.CharField(
        label="Комментарий",
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Дополнительные пожелания (необязательно)'
        })
    )
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['ad'].queryset = Advertisement.objects.filter(owner=user, status='published')        
