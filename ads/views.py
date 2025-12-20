from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from ads.models import Advertisement
from ads.forms import AdvertisementForm


def get_ads_list(request):
  ads = Advertisement.objects.all()
  
  return render(request=request, template_name='ads/ad_list.html', context={'ads': ads})


def get_ad_details(request, ad_slug):
  ad_for_view = get_object_or_404(Advertisement, slug=ad_slug)
  
  return render(request, 'ads/ad_details.html', {'ad': ad_for_view})


@login_required
def create_ad(request):
  title = "Создать объявление"
  submit_button_text = "Опубликовать"
  
  if request.method == "POST":
    form = AdvertisementForm(request.POST, request.FILES)
    if form.is_valid():
      ad = form.save(commit=False)
      ad.owner = request.user
      ad.save()
      return redirect('ads:ad_details', ad_slug=ad.slug)
  else:
      form = AdvertisementForm()
    
  return render(request, 'ads/ad_form.html', {
    'form': form, 
    'title': title,
    'submit_button_text': submit_button_text
    })
  

@login_required 
def update_ad(request, ad_id):
  title = "Редактировать объявление"
  submit_button_text = "Сохранить"
  ad = get_object_or_404(Advertisement, id = ad_id)
  
  if (request.user != ad.owner):
    return render(request, 'ads/not_allowed.html')
  
  if request.method == "POST":
    form = AdvertisementForm(request.POST, request.FILES, instance=ad)
    
    if form.is_valid():
      updated_ad = form.save()
      
      return redirect("ads:ad_details", ad_slug = updated_ad.slug)
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
  

@login_required 
def delete_ad(request, ad_id):
  ad = get_object_or_404(Advertisement, id = ad_id)
  
  if (request.user != ad.owner):
    return render(request, 'ads/not_allowed.html')
  
  if request.method == "POST":
    ad.delete()
    
    return redirect('ads:ad_list')
  
  return render(request, 'ads/confirm_ad_delete.html', {'ad': ad})


def main_page_view(request):
  return render(request, template_name='ads/main_page.html')   