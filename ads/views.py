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
    title = request.POST.get('title').strip()
    text = request.POST.get('text').strip()
    price_str = request.POST.get('price', '').strip()
    contacts = request.POST.get('contacts').strip()
    
    errors = {}
    
    if not title:
      errors['title'] = "Заголовок объявления обязателен!"
    if not text:
      errors['text'] = "Текст объявления обязателен!"
    if not contacts:
            errors['contacts'] = "Контактный телефон обязателен!"
            
    price = None
    if price_str:
            try:
                price = float(price_str)
                if price < 0:
                    errors['price'] = "Цена не может быть отрицательной!"
            except ValueError:
                errors['price'] = "Цена должна быть числом!"        
      
    
    if not errors:
      ad = Advertisement(
      title = title,
      text = text,
      contacts = contacts
    )
      if price is not None:
        ad.price = price
      if 'goods_image' in request.FILES:
        ad.goods_image = request.FILES['goods_image']
      
      ad.save()
    
      return redirect('ad_details', ad_id = ad.id)
    
    else:
      context = {
        'errors': errors,
        'title': title,
        'text': text,
        'price': price_str,
        'contacts': contacts
      }
      return render(request, 'ads/ad_add.html', context)