from django.shortcuts import render, get_object_or_404, redirect
from ads.models import Advertisement
from ads.forms import AdvertisementForm


def get_ads_list(request):
  ads = Advertisement.objects.all()
  
  return render(request=request, template_name='ads/ad_list.html', context={'ads': ads})


def get_ad_details(request, ad_id):
  ad_for_view = get_object_or_404(Advertisement, id=ad_id)
  
  return render(request, 'ads/ad_details.html', {'ad': ad_for_view})


def create_ad(request):
  title = "Создать объявление"
  submit_button_text = "Опубликовать"
  
  if request.method == "POST":
    form = AdvertisementForm(request.POST, request.FILES)
    if form.is_valid():
      ad = form.save()  # Сохраняем в БД
      return redirect('ad_details', ad_id=ad.id)
  else:
      form = AdvertisementForm()
    
  return render(request, 'ads/ad_form.html', {
    'form': form, 
    'title': title,
    'submit_button_text': submit_button_text
    })
  
  
def update_ad(request, ad_id):
  title = "Редактировать объявление"
  submit_button_text = "Сохранить"
  ad = get_object_or_404(Advertisement, id = ad_id)
  
  if request.method == "POST":
    form = AdvertisementForm(request.POST, request.FILES, instance=ad)
    
    if form.is_valid():
      updated_ad = form.save()
      
      return redirect("ad_details", ad_id = updated_ad.id)
    else:
      return render(request, 'ads/ad_form.html', {
        'form': form,
        'title': title,
        'submit_button_text': submit_button_text
        })
    
  form = AdvertisementForm(instance=ad)
  
  return render(request, 'ads/ad_form.html', {
    'form': form,
    'title': title,
    'submit_button_text': submit_button_text
    })
  
  
def delete_ad(request, ad_id):
  get_object_or_404(Advertisement, id = ad_id).delete()
  return redirect('ad_list')    