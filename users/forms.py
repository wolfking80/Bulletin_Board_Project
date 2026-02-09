from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomAuthenticationForm(AuthenticationForm):
  def __init__(self, request= ..., *args, **kwargs):
    super().__init__(request, *args, **kwargs)
      
    self.fields['username'].label = "Email или имя пользователя" 
    self.fields['username'].widget.attrs.update({
      'placeholder': "Введите email или имя пользователя"
    })
    self.error_messages.update({
      'invalid_login': (
        "Пожалуйста, введите корректные email/имя пользователя и пароль. "
        "Обратите внимание, что оба поля могут быть чувствительны к регистру."
      )
    })
    
    
class CustomUserCreationForm(UserCreationForm):
  class Meta:
    model = User
    fields = ("username", "email", "password1", "password2") 
  