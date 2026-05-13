import logging
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.utils import timezone
from django.utils.html import strip_tags  # ДОБАВЛЕН ИМПОРТ

# Настраиваем логгер для текущего файла
logger = logging.getLogger(__name__)

def send_custom_email(subject, template_name, context, to_email, request=None):
    """
    Универсальная отправка HTML-писем с автоматическим определением домена.
    """
    # Подготовка базового контекста (домен, протокол)
    if request:
        current_site = get_current_site(request)
        domain = current_site.domain
        protocol = 'https' if request.is_secure() else 'http'
        site_name = current_site.name
    else:
        # Если запроса нет (например, из сигналов или задач), берем из settings.py
        domain = getattr(settings, 'SITE_DOMAIN', '127.0.0.1:8000')
        protocol = getattr(settings, 'SITE_PROTOCOL', 'http')
        site_name = getattr(settings, 'SITE_NAME', 'Billboard')

    default_context = {
        'domain': domain,
        'protocol': protocol,
        'site_name': site_name,
        'year': timezone.now().year,
    }
    
    # Объединяем контексты (переданный context имеет приоритет)
    full_context = {**default_context, **context}

    try:
        # Рендеринг контента
        html_body = render_to_string(template_name, full_context)
      
        text_body = strip_tags(html_body)

        # Формирование и отправка письма
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to_email]
        )
        msg.attach_alternative(html_body, "text/html")
        
        # Отправляем
        msg.send(fail_silently=False) # Ставим False, чтобы ошибка попала в блок except
        
        logger.info(f"Email '{subject}' успешно отправлен на {to_email}")

    except Exception as e:
        # ДОБАВЛЕНО ЛОГИРОВАНИЕ: теперь в логах будет видна вся ошибка (стек вызова)
        logger.error(
            f"Ошибка при отправке почты на {to_email} (Тема: {subject}): {str(e)}", 
            exc_info=True
        )
