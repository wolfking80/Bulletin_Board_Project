from django.urls import path

from . import views

urlpatterns = [
    path('ads/', views.get_ads_list, name='ad_list'),
    path('ads/<int:ad_id>', views.get_ad_details, name = 'ad_details'), 
    path('ads/add/', views.create_ad, name = 'ad_add'),
    path('ads/<int:ad_id>/edit/', views.update_ad, name='edit_ad'),
    path('ads/<int:ad_id>/delete/', views.delete_ad, name='delete_ad'),
]