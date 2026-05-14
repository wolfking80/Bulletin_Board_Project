from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from asgiref.sync import async_to_sync
from django.conf import settings
from .models import Request
from . import telegram_bot


@receiver(post_save, sender=Request)
def send_telegram_message(sender, instance, created, **kwargs):
    """Мгновенный пуш админу в ТГ при создании новой заявки на платную услугу"""
    if created:
        try:
            # Форматируем дату под часовой пояс проекта
            created_at = instance.created_at.astimezone(timezone.get_current_timezone())
            formatted_date = created_at.strftime("%d-%m-%Y %H:%M")
            user = instance.user

            # Собираем текст в формате Markdown (MD)
            text = (
                f"📦 *Новая заявка на приобретение услуги!*\n\n"
                f"👤 *Пользователь:* {user.username}\n"
                f"📞 *Телефон:* {instance.phone}\n"
                f"💬 *Комментарий:* {instance.comment or 'не указан'}\n\n"
                f"🛠️ *Услуга:* {instance.service.name}\n"
                f"🏷️ *Тип услуги:* {instance.type.name}\n"
                f"💰 *Цена:* {instance.service.price} ₽\n\n"
            )

            if instance.ad:
                text += f"📄 *Объявление:* [{instance.ad.title}]({settings.SITE_URL}/ads/{instance.ad.slug}/)\n"

            text += (
                f"📅 *Дата создания заявки:* {formatted_date}\n\n"
                f"🔗 *Ссылка на админ-панель:* {settings.SITE_URL}/admin/promo/request/{instance.id}/change/"
            )

            # Прямая отправка в Telegram в формате Markdown
            async_to_sync(telegram_bot.send_telegram_message)(
                token=settings.TELEGRAM_BOT_TOKEN,
                chat_id=settings.PERSONAL_CHAT_ID,
                text=text,
                parse_mode="Markdown",
            )

        except Exception:
            # Предотвращаем падение сайта при сбоях сети
            pass
