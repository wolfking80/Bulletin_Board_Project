from django.urls import path
from django.urls import reverse_lazy
from django.contrib.auth import views as auth_views

from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='registration'),
    path('login/', views.CustomLoginView.as_view(), name="login"),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('password-change/', views.CustomPasswordChangeView.as_view(), name='password_change'),
# Можно так:
# path(
#   'password-change/',
#   PasswordChangeView.as_view(
#     template_name='users/pages/password_change.html',
#     success_url=reverse_lazy('users:password_change_done')
#   ),
#   name='password_change'
# ),
    path('password-change/done/', views.PasswordChangeDoneView.as_view(), name='password_change_done'),
# Можно так:
# path('password-change/done/', TemplateView.as_view(template_name='users/pages/password_change_done.html'), name='password_change_done'),
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name="users/pages/password_reset.html",
        email_template_name='users/emails/password_reset.txt',
        html_email_template_name='users/emails/password_reset.html',
        subject_template_name='users/emails/subjects/password_reset.txt',
        success_url=reverse_lazy("users:password_reset_instructions_sent")
    ), name='password_reset'),

    path('password-reset/instructions-sent/', auth_views.PasswordResetDoneView.as_view(
        template_name="users/pages/password_reset_instructions_sent.html"
    ), name='password_reset_instructions_sent'),

    path('password-reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name="users/pages/password_reset_form.html",
        success_url=reverse_lazy('users:password_reset_complete')
    ), name='password_reset_set_new'),

    path('password-reset/complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name="users/pages/password_reset_complete.html"
    ), name='password_reset_complete'),
    path("toggle-theme/", views.toggle_theme, name="toggle_theme"),
    path("<str:username>/", views.ProfileView.as_view(), name='profile'),
]