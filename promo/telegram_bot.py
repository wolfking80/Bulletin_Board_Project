import logging
import telegram

# Лаконичная настройка логов без лишнего мусора
logging.basicConfig(level=logging.INFO)


async def send_telegram_message(token, chat_id, text, parse_mode="Markdown"):
    """Асинхронный шлюз отправки уведомлений в Telegram API"""
    try:
        # Устанавливаем таймаут в 20 секунд на уровне сетевого клиента HTTPX
        # Это поможет при сетевых задержках провайдера
        bot = telegram.Bot(
            token=token,
            get_updates_request=telegram.request.HTTPXRequest(
                connect_timeout=20.0, read_timeout=20.0
            ),
        )

        # Отправляем сообщение
        async with bot:
            await bot.send_message(chat_id=chat_id, text=text, parse_mode=parse_mode)

        logging.info(f"Сообщение успешно отправлено в чат {chat_id}")
    except Exception as e:
        logging.error(f"Ошибка отправки сообщения в чат {chat_id}: {e}")
        raise


# Локальный тест отправки напрямую из терминала
if __name__ == "__main__":
    import os
    import asyncio
    from dotenv import load_dotenv

    load_dotenv()
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    PERSONAL_CHAT_ID = os.getenv("PERSONAL_CHAT_ID")
    test_text = "Тестовое сообщение из Django-приложения платных услуг продвижения"

    asyncio.run(send_telegram_message(TELEGRAM_BOT_TOKEN, PERSONAL_CHAT_ID, test_text))
