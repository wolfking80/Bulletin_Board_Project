from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout



from config.settings import DEFAULT_LOGIN_REDIRECT_URL


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

      next_url = request.GET.get('next', DEFAULT_LOGIN_REDIRECT_URL) # next будет '/posts/add/', например
      return redirect(next_url)
    else:
      return render(request, 'users/login.html', {'form': form})

  form = AuthenticationForm()

  return render(request, 'users/login.html', {'form': form})


def logout_view(request):
  logout(request)
  return redirect("ads:ad_list")
