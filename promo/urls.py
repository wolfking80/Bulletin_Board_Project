from django.urls import path
from . import views
from . import webhooks

app_name = 'promo'

urlpatterns = [
    # Список всех доступных услуг продвижения
    path('', views.ServiceListView.as_view(), name='services_list'),
    
    # Создание заявки на конкретную услугу продвижения
    path('<int:service_id>/requests/create/', views.CreateRequestView.as_view(), name='create_request'),
    
    # Отзывы о конкретной услуге продвижения
    path('<int:service_id>/reviews/', views.ServiceReviewListView.as_view(), name='service_review_list'),
    
    # Оставить отзыв об услуге продвижения
    path('<int:service_id>/reviews/create/', views.CreateReviewView.as_view(), name='create_review'),
    
    #URL ДЛЯ ОПЛАТЫ
    path('service/<int:service_id>/pay/', views.CreatePaymentOrderView.as_view(), name='create_payment_order'),
    path('payment/<int:order_id>/', views.ProcessPaymentView.as_view(), name='process_payment'),
    path('payment-callback/', views.PaymentCallbackView.as_view(), name='payment_callback'),
    path('webhook/yookassa/', webhooks.yookassa_webhook, name='yookassa_webhook'),
]
