from django.db import transaction
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType

from ads.models import Advertisement, AdPromotion, Favorite, AdQuestion
from users.models import Notification


def send_ad_email_task(ad_id, subject, template_name):
    """Отправка email уведомления"""
    from users.utils import send_custom_email

    try:
        ad = Advertisement.objects.select_related("owner").get(pk=ad_id)
        user = ad.owner
        
        # Отправляем на Email, если разрешено
        if user.notifications_enabled and user.email:
            send_custom_email(
                subject=subject,
                template_name=template_name,
                context={"ad": ad, "user": user},
                to_email=user.email,
            )
    except Exception as e:
        print(f"Ошибка в send_ad_email_task: {e}")


@receiver(post_save, sender=Advertisement)
def create_promotion_for_new_ad(sender, instance, created, **kwargs):
    if created:
        AdPromotion.objects.get_or_create(ad=instance)
        
        
# ПЕРЕХВАТЫВАЕМ СТАТУС ФЛАГОВ ДО СОХРАНЕНИЯ В БАЗУ
@receiver(pre_save, sender=AdPromotion)
def capture_old_promo_status(sender, instance, **kwargs):
    if instance.pk:
        try:
            # Загружаем из базы чистые значения до сохранения
            old_obj = sender.objects.only("is_vip", "is_urgent", "is_colored", "is_top").get(pk=instance.pk)
            instance._old_promo_flags = {
                "is_vip": old_obj.is_vip,
                "is_urgent": old_obj.is_urgent,
                "is_colored": old_obj.is_colored,
                "is_top": old_obj.is_top,
            }
        except sender.DoesNotExist:
            instance._old_promo_flags = None        


@receiver(pre_save, sender=Advertisement)
def capture_old_status(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_obj = sender.objects.only("status").get(pk=instance.pk)
            instance._old_status = old_obj.status
        except sender.DoesNotExist:
            instance._old_status = None


@receiver(post_save, sender=Advertisement)
def notify_moderation(sender, instance, created, **kwargs):
    old_status = getattr(instance, "_old_status", None)

    if not created and old_status != "published" and instance.status == "published":
        content_type = ContentType.objects.get_for_model(Advertisement)
        Notification.objects.create(
            recipient=instance.owner,
            sender=None,
            notification_type="moderation_success",
            message=f'Ваше объявление "{instance.title}" прошло модерацию и опубликовано!',
            content_type=content_type,
            object_id=instance.id,
        )
        transaction.on_commit(
            lambda: send_ad_email_task(
                instance.pk,
                "Ваше объявление опубликовано! ✅",
                "users/emails/ad_published.html",
            )
        )

    elif not created and old_status != "rejected" and instance.status == "rejected":
        content_type = ContentType.objects.get_for_model(Advertisement)
        Notification.objects.create(
            recipient=instance.owner,
            sender=None,
            notification_type="moderation_failed",
            message=f'Ваше объявление "{instance.title}" не прошло модерацию.',
            content_type=content_type,
            object_id=instance.id,
        )


@receiver(post_save, sender=AdPromotion)
def notify_promotion(sender, instance, created, **kwargs):
    promo_fields = ["is_vip", "is_urgent", "is_colored", "is_top"]
    old_flags = getattr(instance, "_old_promo_flags", None)

    if created:
        # Если запись только что создана, смотрим на любые активные флаги
        newly_activated = [f for f in promo_fields if getattr(instance, f)]
    elif old_flags:
        # Если это обновление, проверяем: был False, а стал True
        newly_activated = [f for f in promo_fields if getattr(instance, f) and not old_flags.get(f, False)]
    else:
        newly_activated = []

    # Отправляем уведомление ТОЛЬКО если хоть один флаг переключился в True прямо сейчас
    if newly_activated:
        content_type = ContentType.objects.get_for_model(Advertisement)
        services = ", ".join(newly_activated)
        Notification.objects.create(
            recipient=instance.ad.owner,
            sender=None,
            notification_type="promotion",
            message=f'Для объявления "{instance.ad.title}" активированы услуги: {services}',
            content_type=content_type,
            object_id=instance.ad.id,
        )
        transaction.on_commit(
            lambda: send_ad_email_task(
                instance.ad_id,
                "Услуги продвижения активированы! 🚀",
                "users/emails/ad_promo_updated.html",
            )
        )


@receiver(post_save, sender=Favorite)
def create_favorite_notification(sender, instance, created, **kwargs):
    if created and instance.user != instance.ad.owner:
        content_type = ContentType.objects.get_for_model(Advertisement)
        Notification.objects.create(
            recipient=instance.ad.owner,
            sender=instance.user,
            notification_type="favorite",
            message=f'{instance.user.username} добавил ваше объявление "{instance.ad.title}" в избранное',
            content_type=content_type,
            object_id=instance.ad.id,
        )


@receiver(post_save, sender=AdQuestion)
def create_question_notification(sender, instance, created, **kwargs):
    # Уведомление владельцу объявления о новом вопросе
    if created and instance.author != instance.ad.owner:
        content_type = ContentType.objects.get_for_model(Advertisement)
        Notification.objects.create(
            recipient=instance.ad.owner,
            sender=instance.author,
            notification_type="question",
            message=f'{instance.author.username} задал вопрос по объявлению "{instance.ad.title}": {instance.text[:100]}',
            content_type=content_type,
            object_id=instance.ad.id,
        )
