from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from datetime import datetime

def send_custom_email(subject, template_name, context, to_email, request=None):
    if request:
        current_site = get_current_site(request)
        context.update({
            'domain': current_site.domain,
            'protocol': 'https' if request.is_secure() else 'http',
            'site_name': current_site.name,
        })
    else:
        context.setdefault('domain', '127.0.0.1:8000')
        context.setdefault('protocol', 'http')
        context.setdefault('site_name', 'Наш Сервис')

    context['year'] = datetime.now().year

    try:
        html_body = render_to_string(template_name, context)
        msg = EmailMultiAlternatives(
            subject=subject,
            body=subject, # Текстовая заглушка
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to_email]
        )
        msg.attach_alternative(html_body, "text/html")
        msg.send(fail_silently=True)
    except Exception as e:
        print(f"Ошибка почты: {e}")