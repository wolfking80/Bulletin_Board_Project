from django.urls import path

from ads.views import homepage_view

urlpatterns = [
    path('', homepage_view),
]
