from django.urls import path

from . import views

app_name = 'ads'

urlpatterns = [
    path('ads/', views.get_ads_list, name='ad_list'),
    path('ads/category/<slug:category_slug>/', views.get_category_ads, name="ads_category"),
    path('ads/tag/<slug:tag_slug>/', views.get_tag_ads, name="ads_tags"),
    path('ads/add/', views.create_ad, name = 'ad_add'),
    path('ads/<int:ad_id>/edit/', views.update_ad, name='edit_ad'),
    path('ads/<int:ad_id>/delete/', views.delete_ad, name='delete_ad'),
    path('ads/<slug:ad_slug>', views.get_ad_details, name = 'ad_details'), 
    path('', views.main_page_view, name='main_page'),
]