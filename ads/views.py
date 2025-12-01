from django.shortcuts import render, get_object_or_404, redirect
from ads.models import Advertisement


def get_ads_list(request):
  ads = Advertisement.objects.all()
  
  return render(request=request, template_name='ads/ad_list.html', context={'ads': ads})


def get_ad_details(request, ad_id):
  ad_for_view = get_object_or_404(Advertisement, id=ad_id)
  
  return render(request, 'ads/ad_details.html', {'ad': ad_for_view})


def create_ad(request):
  if request.method == "GET":
    return render(request, 'ads/ad_add.html')
  
  if request.method == "POST":
    ad = Advertisement(
      title = request.POST.get('title'),
      text = request.POST.get('text'),
      price = request.POST.get('price'),
      contacts = request.POST.get('contacts')
    )
    if 'goods_image' in request.FILES:
      ad.goods_image = request.FILES['goods_image']
      
    ad.save()
      
    return redirect('ad_details', ad_id = ad.id)
