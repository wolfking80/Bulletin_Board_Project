# promo/services.py
from decimal import Decimal
from uuid import uuid4
from yookassa import Configuration, Payment
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class YooKassaPaymentService:
    """Сервис для работы с YooKassa API"""

    def __init__(self):
        if not settings.YOOKASSA_SHOP_ID or not settings.YOOKASSA_SECRET_KEY:
            raise RuntimeError("Задайте YOOKASSA_SHOP_ID и YOOKASSA_SECRET_KEY в .env")

        Configuration.account_id = settings.YOOKASSA_SHOP_ID
        Configuration.secret_key = settings.YOOKASSA_SECRET_KEY

    def create_payment(self, payment_order, return_url=None):
        """
        Создаёт платёж в YooKassa

        Args:
            payment_order: объект PaymentOrder
            return_url: URL для редиректа после оплаты

        Returns:
            dict: {'payment_id': '...', 'confirmation_url': '...', 'status': '...'}
        """
        return_url = return_url or settings.YOOKASSA_RETURN_URL

        description = f"Оплата услуги '{payment_order.service.name}'"
        if payment_order.ad:
            description += f" для объявления #{payment_order.ad.id}"

        # Формируем payload для YooKassa
        payload = {
            "amount": {
                "value": f"{payment_order.amount:.2f}",
                "currency": "RUB",
            },
            "confirmation": {
                "type": "redirect",
                "return_url": return_url,
            },
            "capture": True,
            "description": description[:128],
            "metadata": {
                "payment_order_id": payment_order.id,
                "service_id": payment_order.service.id,
                "user_id": payment_order.user.id,
            },
            "receipt": {
                "customer": {
                    "email": payment_order.user.email
                    or f"user_{payment_order.user.id}@example.com",
                },
                "items": [
                    {
                        "description": payment_order.service.name[:128],
                        "quantity": "1.00",
                        "amount": {
                            "value": f"{payment_order.amount:.2f}",
                            "currency": "RUB",
                        },
                        "vat_code": 1,
                        "payment_mode": "full_prepayment",
                        "payment_subject": "service",
                    },
                ],
            },
        }

        try:
            payment = Payment.create(payload, str(uuid4()))

            payment_order.payment_id = payment.id
            payment_order.save(update_fields=["payment_id"])

            return {
                "payment_id": payment.id,
                "confirmation_url": payment.confirmation.confirmation_url,
                "status": payment.status,
            }
        except Exception as e:
            logger.error(f"Ошибка создания платежа YooKassa: {e}")
            raise
