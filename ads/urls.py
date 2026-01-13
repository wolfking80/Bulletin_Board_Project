from django.urls import path

from . import views

app_name = 'ads'

urlpatterns = [
    path('', views.MainPageView.as_view(), name='main_page'),
    path('ads/', views.AdsListView.as_view(), name='ad_list'),
    path('ads/search/', views.AdSearchView.as_view(), name='ad_search'),
    path('ads/create/', views.AdCreateView.as_view(), name='create_ad'),
    path('ads/category/<slug:category_slug>/', views.CategoryAdsListView.as_view(), name='category_ads'),
    path('ads/tag/<slug:tag_slug>/', views.TagAdsListView.as_view(), name='tag_ads'),
    path('ads/<slug:ad_slug>/', views.AdDetailView.as_view(), name='ad_details'),
    path('ads/<int:pk>/update/', views.AdUpdateView.as_view(), name='update_ad'),
    path('ads/<int:pk>/delete/', views.AdDeleteView.as_view(), name='delete_ad'),
    path('favorite/<int:ad_id>/', views.toggle_favorite, name='toggle_favorite'),
    path('my-favorites/', views.MyFavoritesView.as_view(), name='my_favorites'),
]