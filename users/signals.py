from django.db import transaction
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from ads.models import Advertisement, AdPromotion, Favorite
from users.models import Notification
from users.utils import send_custom_email


def send_ad_email(ad_id, subject, template_name):
    from ads.models import Advertisement
    try:
        ad = Advertisement.objects.select_related('owner').get(pk=ad_id)
        user = ad.owner
        
        # Создаем внутреннее уведомление
        Notification.objects.create(
            user=user,
            ad=ad,
            message=subject
        )
        
        if user.notifications_enabled and user.email:
            context = {'ad': ad, 'user': user}
            send_custom_email(
                subject=subject,
                template_name=template_name,
                context=context,
                to_email=user.email
            )
    except Exception as e:
        print(f"Ошибка в сигнале: {e}")
        
        
# АВТОМАТИЧЕСКОЕ СОЗДАНИЕ ЗАПИСИ ПРОДВИЖЕНИЯ
@receiver(post_save, sender=Advertisement)
def create_promotion_for_new_ad(sender, instance, created, **kwargs):
    if created:
        # Создаем пустую запись в таблице промо, чтобы JOIN в SQL не ломался
        AdPromotion.objects.get_or_create(ad=instance) 

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
        

# СИГНАЛ ОПОВЕЩЕНИЯ ПОЛЬЗОВАТЕЛЯ
@receiver(post_save, sender=Favorite)
def create_favorite_notification(sender, instance, created, **kwargs):
    if created and instance.user != instance.ad.owner:
        Notification.objects.create(
            user=instance.ad.owner,
            ad=instance.ad,
            message=f"Пользователь {instance.user.username} добавил ваше объявление «{instance.ad.title}» в избранное ★")