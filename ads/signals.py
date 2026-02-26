from django.db import transaction
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.contrib.auth import get_user_model
from .models import Advertisement, AdPromotion


# ФУНКЦИЯ (запускается ТОЛЬКО после того, как БД всё сохранила)
def send_ad_email(ad_id, subject, template_name):
    User = get_user_model()
    # Делаем ПАУЗУ и берем данные из базы, когда транзакция уже закрыта
    try:
        from .models import Advertisement
        ad = Advertisement.objects.select_related('owner').get(pk=ad_id)
        user = ad.owner
        
        # Теперь база 100% отдает True, если включить галочку в другой вкладке
        if user.notifications_enabled and user.email:
            context = {'ad': ad, 'user': user, 'protocol': 'http', 'domain': '127.0.0.1:8000'}
            html_body = render_to_string(template_name, context)
            msg = EmailMultiAlternatives(subject=subject, body=f"Обновление: {ad.title}", to=[user.email])
            msg.attach_alternative(html_body, "text/html")
            msg.send(fail_silently=True)
    except Exception as e:
        print(f"Ошибка отправки почты: {e}") 

# СИГНАЛ МОДЕРАЦИИ
@receiver(pre_save, sender=Advertisement)
def capture_old_status(sender, instance, **kwargs):
    if instance.pk:
        # Запоминаем текущий статус в БД
        instance._old_status = Advertisement.objects.filter(pk=instance.pk).values_list('status', flat=True).first()

@receiver(post_save, sender=Advertisement)
def notify_moderation(sender, instance, created, **kwargs):
    old_status = getattr(instance, '_old_status', None)
    if not created and old_status != 'published' and instance.status == 'published':
        # для DJANGO: чтобы сначала сохранил всё в базу, и только ПОТОМ выслал письмо
        transaction.on_commit(lambda: send_ad_email(instance.pk, "Ваше объявление опубликовано! ✅", "users/emails/ad_published.html"))

# СИГНАЛ ПРОДВИЖЕНИЯ
@receiver(post_save, sender=AdPromotion)
def notify_promotion(sender, instance, created, **kwargs):
    if any([instance.is_vip, instance.is_urgent, instance.is_colored, instance.is_top]):
        # Ждем фиксации транзакции в базе
        transaction.on_commit(lambda: send_ad_email(instance.ad_id, "Услуги продвижения активированы! 🚀", "users/emails/ad_promo_updated.html"))