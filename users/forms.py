from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = "Email или имя"
        self.fields['username'].widget.attrs.update({
            'placeholder': "Введите email или имя пользователя",
            'class': 'form-control'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control'
        })

    def confirm_login_allowed(self, user):
        # Проверки на возможность входа пользователя на сайт
        if not user.is_active:
            raise ValidationError(
                "Аккаунт заблокирован администратором.", 
                code='banned'
            )
        if not user.email_confirmed:
            raise ValidationError(
                "Почта не подтверждена! Проверьте свой почтовый ящик.", 
                code='not_activated'
            )

class CustomUserCreationForm(UserCreationForm):
    # Явно добавляем email как обязательное поле
    email = forms.EmailField(
        required=True, 
        help_text="Обязательно для активации аккаунта"
    )

    class Meta(UserCreationForm.Meta):
        model = User
        # Пароли UserCreationForm добавит сама, здесь только основные данные
        fields = ("username", "email")

    def clean_email(self):
        # Проверка уникальности почты
        email = self.cleaned_data.get('email').lower()
        if User.objects.filter(email=email).exists():
            raise ValidationError("Пользователь с такой почтой уже зарегистрирован.")
        return email 
  