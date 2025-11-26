from django.shortcuts import render
from ads.models import Advertisement


def get_ads_list(request):
  ads = Advertisement.objects.all()
  
  return render(request=request, template_name='ads/ad_list.html', context={'ads': ads})
