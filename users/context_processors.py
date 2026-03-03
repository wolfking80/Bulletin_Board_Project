from django.utils import timezone
from datetime import timedelta


def current_theme(request):
  if request.user.is_authenticated:
    return {'current_theme': request.user.selected_theme}

  return {'current_theme': request.session.get('theme', 'dark')}


def notifications_count(request):
  if request.user.is_authenticated:
  # Удаляем всё, что старше 30 дней
    request.user.notifications.filter(
      created_at__lt=timezone.now() - timedelta(days=30)
    ).delete()

  # Считаем только живые и непрочитанные
    count = request.user.notifications.filter(is_read=False).count()
    return {'unread_notifications_count': count}
    
  return {'unread_notifications_count': 0}