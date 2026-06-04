from django.urls import path
from django.urls import reverse_lazy
from django.contrib.auth import views as auth_views

from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='registration'),
    path('toggle-notifications/', views.toggle_notifications, name='toggle_notifications'),
    path('activate-account/<uidb64>/<token>/', views.activate_account_view, name='activate_account'),
    path('login/', views.CustomLoginView.as_view(), name="login"),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('phone-number/set/', views.set_phone_number, name='set_phone_number'),
    path('phone-number/mark-verified/', views.mark_phone_number_as_verified, name='mark_phone_number_as_verified'),
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
    path('my/password-reset/', views.ProfilePasswordResetView.as_view(), name="profile_password_reset"),

    path('my/password-reset/instructions-sent/', auth_views.PasswordResetDoneView.as_view(
        template_name="users/pages/password_reset_profile_instructions_sent.html"
    ), name='profile_password_reset_instructions_sent'),
    path("toggle-theme/", views.toggle_theme, name="toggle_theme"),
    path('settings/', views.SettingsView.as_view(), name='settings'),
    # API уведомлений
    path('notifications/', views.NotificationListViewJSON.as_view(), name='notifications_json'),
    path('notifications/mark-read/<int:pk>/', views.MarkNotificationReadView.as_view(), name='mark_notification_read'),
    path('notifications/mark-all-read/', views.MarkAllNotificationsReadView.as_view(), name='mark_all_read'),
    path('notifications/unread-count/', views.UnreadNotificationsCountView.as_view(), name='unread_count'),
    path('notifications/delete/<int:pk>/', views.DeleteNotificationView.as_view(), name='delete_notification'),
    path('notifications/delete-all/', views.DeleteAllNotificationsView.as_view(), name='delete_all_notifications'),
    
    path('notifications/all/', views.NotificationListView.as_view(), name='notifications'),
    path('notifications/read/<int:notification_id>/', views.read_and_redirect, name='read_notification'),
    path("<str:username>/", views.ProfileView.as_view(), name='profile'),
]