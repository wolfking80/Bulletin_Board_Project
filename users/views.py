from django.views.generic.list import MultipleObjectMixin
from django.contrib.auth import get_user_model

from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, TemplateView
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordResetView

from config.settings import DEFAULT_LOGIN_REDIRECT_URL
from users.forms import CustomAuthenticationForm, CustomUserCreationForm
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST

User = get_user_model()


class RegisterView(CreateView):
  template_name = 'users/pages/register.html'
  form_class = CustomUserCreationForm
  success_url = reverse_lazy('users:login')


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


class ProfileView(DetailView, MultipleObjectMixin):
  model = User
  slug_url_kwarg = 'username'
  slug_field = 'username'
  template_name = 'users/pages/index.html'
  context_object_name = 'user'
  paginate_by = 3  
  
  def get_context_data(self, **kwargs):
    ads = self.object.ads.order_by('-created_at')
    # Заполняем queryset, чтобы django было что пагинировать
    context = super().get_context_data(object_list=ads, **kwargs)
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
    context['ads'] = context['object_list']
    del context['object_list']
    
    return context
