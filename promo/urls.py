from django.urls import path
from . import views

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
]
