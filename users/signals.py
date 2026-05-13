from django.db import transaction
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.db.models import F

# Импортируем только то, что точно не вызовет циклов
from ads.models import Advertisement, AdPromotion, Favorite

def send_ad_email_task(ad_id, subject, template_name):
    """
    Вынесено в отдельную функцию для удобства тестирования и 
    возможного переноса в Celery (фоновые задачи)
    """
    from users.models import Notification
    from users.utils import send_custom_email
    
    try:
        ad = Advertisement.objects.select_related('owner').get(pk=ad_id)
        user = ad.owner

        # Создаем уведомление в БД
        Notification.objects.create(
            user=user,
            ad=ad,
            message=subject
        )

        # Отправляем на Email, если разрешено
        if user.notifications_enabled and user.email:
            send_custom_email(
                subject=subject,
                template_name=template_name,
                context={'ad': ad, 'user': user},
                to_email=user.email
            )
    except Exception as e:
        # В идеале здесь должно быть логирование (logger.error)
        print(f"Ошибка в send_ad_email_task: {e}")

@receiver(post_save, sender=Advertisement)
def create_promotion_for_new_ad(sender, instance, created, **kwargs):
    # Автоматическая инициализация записи промо при создании объявления
    if created:
        AdPromotion.objects.get_or_create(ad=instance)

@receiver(pre_save, sender=Advertisement)
def capture_old_status(sender, instance, **kwargs):
    # Сохраняем старый статус до того, как он запишется в базу
    if instance.pk:
        try:
            # Делаем values_list('status'), чтобы не тянуть весь объект
            old_obj = sender.objects.only('status').get(pk=instance.pk)
            instance._old_status = old_obj.status
        except sender.DoesNotExist:
            instance._old_status = None

@receiver(post_save, sender=Advertisement)
def notify_moderation(sender, instance, created, **kwargs):
    # Уведомление при успешном прохождении модерации
    old_status = getattr(instance, '_old_status', None)
    
    # Срабатывает только если статус сменился на 'published'
    if not created and old_status != 'published' and instance.status == 'published':
        transaction.on_commit(lambda: send_ad_email_task(
            instance.pk, 
            "Ваше объявление опубликовано! ✅", 
            "users/emails/ad_published.html"
        ))

@receiver(post_save, sender=AdPromotion)
def notify_promotion(sender, instance, created, **kwargs):
    # Уведомление об активации платных услуг
    # Список полей для проверки
    promo_fields = ['is_vip', 'is_urgent', 'is_colored', 'is_top']
    
    # Проверяем, было ли что-то активировано (если запись только создана или изменена)
    if any(getattr(instance, field) for field in promo_fields):
        # Чтобы не спамить при каждом обновлении, можно добавить проверку 
        # на то, что это именно ПЕРВОЕ включение (через pre_save аналогично статусу)
        transaction.on_commit(lambda: send_ad_email_task(
            instance.ad_id, 
            "Услуги продвижения активированы! 🚀", 
            "users/emails/ad_promo_updated.html"
        ))

@receiver(post_save, sender=Favorite)
def create_favorite_notification(sender, instance, created, **kwargs):
    # Уведомление владельцу, что его объявление оценили
    from users.models import Notification
    
    if created and instance.user != instance.ad.owner:
        Notification.objects.create(
            user=instance.ad.owner,
            ad=instance.ad,
            message=f"Ваше объявление «{instance.ad.title}» добавили в избранное ★"
        )
