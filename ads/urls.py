from django.urls import path

from . import views

urlpatterns = [
    path('ads/', views.get_ads_list),
    path('ads/<int:ad_id>', views.get_ad_details, name = 'ad_details'), 
]
