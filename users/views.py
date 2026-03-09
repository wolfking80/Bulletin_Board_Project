from django.contrib.auth import get_user_model

from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, TemplateView, ListView
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordResetView
from django.contrib import messages
from django.http import JsonResponse
from phonenumber_field.phonenumber import PhoneNumber
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from datetime import timedelta

from users.models import Notification

from config.settings import DEFAULT_LOGIN_REDIRECT_URL, FIREBASE_API_KEY
from users.forms import CustomAuthenticationForm, CustomUserCreationForm
from users.utils import send_custom_email


User = get_user_model()


class RegisterView(CreateView):
  template_name = 'users/pages/register.html'
  form_class = CustomUserCreationForm
  
  def form_valid(self, form):
    # Сохраняем пользователя как неактивного
    user = form.save(commit=False)
    user.email_confirmed = False
    user.save()
      
    # Отправляем письмо активации
    self.send_activation_email(user)
      
    messages.success(
      self.request,
      "Регистрация прошла успешно! Проверьте почту для активации аккаунта."
    )
    # Используем явный редирект, чтобы избежать повторного form.save() в super().form_valid(form)
    # второй save() менял пользователя и делал token недействительным  
    return redirect('users:login')
  
  def send_activation_email(self, user):
    token = default_token_generator.make_token(user)
    uidb64 = urlsafe_base64_encode(force_bytes(user.id))
    activation_url = self.request.build_absolute_uri(
        reverse_lazy('users:activate_account', kwargs={'uidb64': uidb64, 'token': token})
    )
    
    send_custom_email(
        subject='Активация аккаунта',
        template_name='users/emails/activation.html',
        context={'user': user, 'activation_url': activation_url},
        to_email=user.email,
        request=self.request
    )
    

def activate_account_view(request, uidb64, token):
  try:
    uid = force_str(urlsafe_base64_decode(uidb64))  
    user = User.objects.get(pk=uid)
  except(TypeError, ValueError, User.DoesNotExist):
    user = None
    
  if user and default_token_generator.check_token(user, token):
    user.email_confirmed = True
    user.save()
    messages.success(request, 'Аккаунт успешно активирован! Теперь Вы можете войти.')
    return redirect('users:login')  
  else:
    messages.error(request, 'Ссылка активации недействительна или устарела!')
    return redirect('users:registration')


class CustomLoginView(LoginView):
  template_name = 'users/pages/login.html'
  authentication_form = CustomAuthenticationForm
  
  def get_success_url(self):
    next_url = self.request.GET.get('next', DEFAULT_LOGIN_REDIRECT_URL)
    if next_url == DEFAULT_LOGIN_REDIRECT_URL:
      return reverse_lazy(next_url, kwargs={'username': self.request.user.username})
    return next_url
  
  def form_invalid(self, form):
    messages.warning(self.request, 'Ошибка входа!')
    return super().form_invalid(form)
  
  
class CustomLogoutView(LogoutView):
  next_page = reverse_lazy('ads:ad_list')
  
  

@require_POST
@login_required
def set_phone_number(request):
  try:
    # Преобразуем строку в объект PhoneNumber
    parsed_phone_number = PhoneNumber.from_string(request.POST.get('phone_number'), region='RU')
    if parsed_phone_number.is_valid():
      # Проверяем, не пытается ли пользователь установить заново свой же номер телефона
      if request.user.phone_number == parsed_phone_number:
        messages.info(request, 'Этот номер телефона уже привязан к вашему аккаунту')
        return redirect('users:settings')
      
      # Проверяем, не подтвержден ли этот номер телефона у другого пользователя
      user_verified_this_number = User.objects.filter(
        phone_number=parsed_phone_number,
        phone_number_verified=True
      )
      
      if user_verified_this_number.exists():
        messages.warning(request, 'Этот номер телефона уже используется другим пользователем')
        return redirect('users:settings')

      # Определяем сообщение в зависимости от того, был ли номер телефона до этого
      if request.user.phone_number:
        message = 'Номер телефона успешно изменён'
      else:
        message = 'Номер телефона успешно добавлен'

      request.user.phone_number = parsed_phone_number
      request.user.phone_number_verified = False  # Сбрасываем статус верификации (если до этого номер телефона был верифицирован)
      request.user.save()
      messages.success(request, message)
    else:
      messages.warning(request, 'Некорректный формат номера телефона')
  except:
    messages.warning(request, 'Указанное вами, похоже, не является номером телефона.')
  
  return redirect('users:settings')


@require_POST
@login_required
def mark_phone_number_as_verified(request):
  # В JS мы уже проверили код
  # Обновляем статус верификации номера телефона
  request.user.phone_number_verified = True
  request.user.save()

  # Удаляем этот номер телефона у других пользователей
  users_not_verified_this_number = User.objects.filter(
    phone_number=request.user.phone_number
  ).exclude(id=request.user.id)

  if users_not_verified_this_number.exists():
    for user in users_not_verified_this_number:
      user.phone_number = None
      user.save()
  
  return JsonResponse({'success': True})
  
  
class CustomPasswordChangeView(PasswordChangeView):
  template_name = 'users/pages/password_change.html'
  success_url = reverse_lazy('users:password_change_done')
  
  def form_valid(self, form):
    messages.success(self.request, 'Пароль успешно изменен!')
    return super().form_valid(form)


class PasswordChangeDoneView(TemplateView):
  template_name = 'users/pages/password_change_done.html'
  
  
class ProfilePasswordResetView(PasswordResetView):
  template_name="users/pages/password_reset_profile.html"
  email_template_name='users/emails/password_reset.txt',
  html_email_template_name='users/emails/password_reset.html',
  subject_template_name='users/emails/subjects/password_reset.txt'
  success_url=reverse_lazy("users:profile_password_reset_instructions_sent")

  def post(self, request, *args, **kwargs):
    request.POST = request.POST.copy()
    request.POST['email'] = request.user.email

    messages.success(request, f'Письмо отправлено на {request.user.email}')

    return super().post(request, *args, **kwargs)  
  

@require_POST
def toggle_theme(request):
  if request.user.is_authenticated:
    # Для авторизованных — меняем в базе
    new_theme = 'light' if request.user.selected_theme == 'dark' else 'dark'
    request.user.selected_theme = new_theme
    request.user.save(update_fields=["selected_theme"])
  else:
    # Для неавторизованных — меняем в сессии
    current_theme = request.session.get('theme', 'dark')
    new_theme = 'light' if current_theme == 'dark' else 'dark'
    request.session['theme'] = new_theme
  
  return JsonResponse({'new_theme': new_theme})


class SettingsView(TemplateView):
  """Страница настроек профиля"""
  template_name = 'users/pages/settings.html'
  extra_context = {
    'FIREBASE_API_KEY': FIREBASE_API_KEY,
  }


class ProfileView(DetailView):
  model = User
  slug_url_kwarg = 'username'
  slug_field = 'username'
  template_name = 'users/pages/index.html'
  context_object_name = 'user' 
  
  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    # Проверяем, мой профиль или чужой
    is_owner = self.request.user == self.object
    # Формируем запрос
    ads_qs = self.object.ads.all()
    if not is_owner:
      # В чужом профиле — только опубликованные
      ads_qs = ads_qs.filter(status='published')
    
    ads_qs = ads_qs.order_by('-created_at')

    # Настройки для BatchLoader
    context['ads'] = ads_qs[:3]
    context['has_more_ads'] = ads_qs.count() > 3
    context['ads_per_batch'] = 3
    context['owner_id'] = self.object.id
    # Флаг для JS, чтобы он знал, можно ли подтягивать неопубликованные
    context['show_all'] = is_owner
    
    pos = self.object.received_ratings.filter(is_positive=True).count()
    neg = self.object.received_ratings.filter(is_positive=False).count()
    total = pos + neg
    
    context['pos_rating'] = pos
    context['neg_rating'] = neg
    
    if total > 0:
      context['trust_percent'] = round((pos / total) * 100)
      context['neg_percent'] = 100 - context['trust_percent']
    else:
      context['trust_percent'] = 0
      context['neg_percent'] = 0
    if self.request.user.is_authenticated:
      user_rating = self.object.received_ratings.filter(voter=self.request.user).first()
      context['user_choice'] = 'plus' if user_rating and user_rating.is_positive else \
                                'minus' if user_rating else 'none'
    
    return context
  
  
class NotificationListView(LoginRequiredMixin, ListView):
  model = Notification
  template_name = 'users/pages/notifications.html'
  context_object_name = 'notifications'

  def get_queryset(self):
    # Удаляем всё, что старше 30 дней
    self.request.user.notifications.filter(
      created_at__lt=timezone.now() - timedelta(days=30)
    ).delete()
    # Показываем последние 20 уведомлений пользователя
    return self.request.user.notifications.all()[:20]

  def post(self, request, *args, **kwargs):
    # При нажатии "Прочитать всё" — сбрасываем счетчик
    self.request.user.notifications.filter(is_read=False).update(is_read=True)
    return redirect('users:notifications')


@login_required
@require_POST
def toggle_notifications(request):
  user = request.user
  # Переключаем флаг
  user.notifications_enabled = not user.notifications_enabled
  user.save()
  return JsonResponse({'notifications_enabled': user.notifications_enabled})