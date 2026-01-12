from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='registration'),
    path('login/', views.CustomLoginView.as_view(), name="login"),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path("<str:username>/", views.ProfileView.as_view(), name='profile'),
]