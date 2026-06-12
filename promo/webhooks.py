# promo/webhooks.py
import ipaddress
import json
import logging
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponseBadRequest
from django.utils import timezone
from yookassa.domain.notification import WebhookNotification

from .models import PaymentOrder

logger = logging.getLogger(__name__)

# IP-адреса YooKassa
YOOKASSA_IP_RANGES = [
    "185.71.76.0/27",
    "185.71.77.0/27",
    "77.75.153.0/25",
    "77.75.156.11",
    "77.75.156.35",
    "77.75.154.128/25",
    "2a02:5180::/32",
]


def is_yookassa_ip(request_ip):
    """Проверка, что запрос пришёл с IP YooKassa"""
    if not request_ip:
        return False

    try:
        ip = ipaddress.ip_address(request_ip)
    except ValueError:
        return False

    for ip_range in YOOKASSA_IP_RANGES:
        if "/" in ip_range:
            if ip in ipaddress.ip_network(ip_range, strict=False):
                return True
        else:
            if ip == ipaddress.ip_address(ip_range):
                return True
    return False


@csrf_exempt
@require_POST
def yookassa_webhook(request):
    """Эндпоинт для приёма уведомлений от YooKassa"""

    # Проверка IP
    client_ip = request.META.get("HTTP_X_FORWARDED_FOR", "").split(",")[0].strip()
    if not client_ip:
        client_ip = request.META.get("REMOTE_ADDR")

    if not settings.DEBUG and not is_yookassa_ip(client_ip):
        logger.warning(f"Webhook с неразрешённого IP: {client_ip}")
        return JsonResponse({"error": "IP not allowed"}, status=403)

    # Чтение тела запроса
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON: {e}")
        return HttpResponseBadRequest("Invalid JSON")

    # Валидация через SDK
    try:
        notification = WebhookNotification(payload)
    except Exception as e:
        logger.error(f"Invalid notification: {e}")
        return HttpResponseBadRequest(f"Invalid notification: {e}")

    payment = notification.object
    metadata = payment.metadata or {}
    payment_order_id = metadata.get("payment_order_id")

    if not payment_order_id:
        logger.error("Missing payment_order_id in metadata")
        return JsonResponse({"status": "ignored", "reason": "missing payment_order_id"})

    # Находим заказ
    try:
        payment_order = PaymentOrder.objects.get(id=int(payment_order_id))
    except PaymentOrder.DoesNotExist:
        logger.warning(f"PaymentOrder {payment_order_id} not found")
        return JsonResponse({"status": "ignored", "reason": "order not found"})

    # Обработка статуса
    if payment.status == "succeeded" and payment_order.status != "paid":
        payment_order.status = "paid"
        payment_order.paid_at = timezone.now()
        payment_order.save()

        # Активируем услугу
        payment_order.activate_service()

        logger.info(f"Платёж #{payment_order.id} успешно оплачен")

    elif payment.status == "canceled" and payment_order.status == "pending":
        payment_order.status = "canceled"
        payment_order.save()
        logger.info(f"Платёж #{payment_order.id} отменён")

    return JsonResponse({"status": "ok"})
