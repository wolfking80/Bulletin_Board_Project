from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('ads.urls')),
    path('promo/', include('promo.urls')),
    path('profile/', include('users.urls')),
    
    path('terms/', TemplateView.as_view(template_name='legal/terms.html'), name='terms_of_use'),
    path('privacy/', TemplateView.as_view(template_name='legal/privacy.html'), name='privacy_policy'),
    path('contacts/', TemplateView.as_view(template_name='legal/contacts.html'), name='contacts'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
