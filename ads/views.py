from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from ads.models import Advertisement, Category, Tag
from ads.forms import AdvertisementForm


def get_ads_list(request):
  ads = Advertisement.objects.filter(status="published")
  
  return render(request=request, template_name='ads/pages/ad_list.html', context={'ads': ads})


def get_category_ads(request, category_slug):
  category = get_object_or_404(Category, slug=category_slug)
  ads = Advertisement.objects.filter(category=category, status='published')
  
  context = {
    'category': category,
    'ads': ads
  }
  return render(request, 'ads/pages/ads_category.html', context)


def get_tag_ads(request, tag_slug):
  tag = get_object_or_404(Tag, slug=tag_slug)
  ads = Advertisement.objects.filter(tags=tag, status='published')

  return render(request, 'ads/pages/ad_tags.html', {
    'tag': tag,
    'ads': ads
  })


def get_ad_details(request, ad_slug):
  ad_for_view = get_object_or_404(Advertisement, slug=ad_slug)
  
  return render(request, 'ads/pages/ad_details.html', {'ad': ad_for_view})


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
      form.save_m2m()
      return redirect('ads:ad_details', ad_slug=ad.slug)
  else:
      form = AdvertisementForm()
    
  return render(request, 'ads/pages/ad_form.html', {
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
    return render(request, 'ads/pages/not_allowed.html')
  
  if request.method == "POST":
    form = AdvertisementForm(request.POST, request.FILES, instance=ad)
    
    if form.is_valid():
      updated_ad = form.save()
      
      return redirect("ads:ad_details", ad_slug = updated_ad.slug)
    else:
      return render(request, 'ads/pages/ad_form.html', {
        'form': form,
        'title': title,
        'submit_button_text': submit_button_text
        })
    
  form = AdvertisementForm(instance=ad)
  
  return render(request, 'ads/pages/ad_form.html', {
    'form': form,
    'title': title,
    'submit_button_text': submit_button_text
    })
  

@login_required 
def delete_ad(request, ad_id):
  ad = get_object_or_404(Advertisement, id = ad_id)
  
  if (request.user != ad.owner):
    return render(request, 'ads/pages/not_allowed.html')
  
  if request.method == "POST":
    ad.delete()
    
    return redirect('ads:ad_list')
  
  return render(request, 'ads/pages/confirm_ad_delete.html', {'ad': ad})


def main_page_view(request):
  return render(request, template_name='ads/pages/main_page.html')   