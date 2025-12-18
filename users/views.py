from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, get_user_model

from ads.models import Advertisement

from config.settings import DEFAULT_LOGIN_REDIRECT_URL

User = get_user_model()


def register_view(request):
  if request.method == 'POST':
    form = UserCreationForm(request.POST)
    
    if form.is_valid():
      form.save()
      return redirect('users:login')
    else:
      return render(request, 'users/register.html', {'form': form})
    
  form = UserCreationForm()
  
  return render(request, 'users/register.html', {'form': form})


def login_view(request):
  if request.method == "POST":
    form = AuthenticationForm(data=request.POST)
    if form.is_valid():
      login(request, form.get_user())

      next_url = request.GET.get('next', DEFAULT_LOGIN_REDIRECT_URL)
      if next_url == DEFAULT_LOGIN_REDIRECT_URL:
        return redirect(next_url, request.user.username)
      else:
        return redirect(next_url)
    else:
      return render(request, 'users/login.html', {'form': form})

  form = AuthenticationForm()

  return render(request, 'users/login.html', {'form': form})


def logout_view(request):
  logout(request)
  return redirect("ads:ad_list")


def profile_view(request, username):
  user = get_object_or_404(User, username=username)
  ads = user.ads.order_by('-created_at')

  context = {
    'user': user,
    'ads': ads
  }

  return render(request, 'users/profile.html', context)
