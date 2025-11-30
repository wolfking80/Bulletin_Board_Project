from django.shortcuts import render, get_object_or_404
from ads.models import Advertisement


def get_ads_list(request):
  ads = Advertisement.objects.all()
  
  return render(request=request, template_name='ads/ad_list.html', context={'ads': ads})


def get_ad_details(request, ad_id):
  ad_for_view = get_object_or_404(Advertisement, id=ad_id)
  
  return render(request, 'ads/ad_details.html', {'ad': ad_for_view})
