from django.urls import path

from . import views

urlpatterns = [
    path('ads/', views.get_ads_list),
]
