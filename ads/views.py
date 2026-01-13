from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from django.db.models import F, Q

from ads.models import Advertisement, Category, Tag, Favorite
from ads.forms import AdvertisementForm
from .mixins import FavoriteMixin 



class AdsListView(FavoriteMixin, ListView):                # Создаем класс на основе ListView
  model = Advertisement                    # Указываем модель для работы
  context_object_name = 'ads'              # Имя переменной в шаблоне
  template_name = 'ads/pages/ad_list.html' # Путь к шаблону
  queryset = Advertisement.objects.filter(status="published").order_by('created_at')  # Фильтрация
  paginate_by = 3
  
  
class AdSearchView(ListView):
  template_name = 'ads/pages/ad_search.html'
  context_object_name = 'ads'
  
  def get_context_data(self, **kwargs):
      context = super().get_context_data(**kwargs)
      context["search_performed"] = any(self.request.GET.keys())
      return context
    
  def get_queryset(self):
    search_query = self.request.GET.get('search')
    
    if search_query:
      queryset = Advertisement.objects.filter(status='published')
      search_category = self.request.GET.get('search_category')
      search_tag = self.request.GET.get('search_tag')
      
      query = Q(title__icontains=search_query) | Q(text__icontains=search_query)

      if search_category:
        query |= Q(category__name__icontains=search_query)
        
      if search_tag:
        query |= Q(tags__name__icontains=search_query)
        
      return queryset.filter(query).order_by('-created_at')  
          
    return Advertisement.objects.none()
    

class CategoryAdsListView(FavoriteMixin, ListView):        # Класс для списка по категории
  template_name = 'ads/pages/ads_category.html'  # Шаблон для категории
  context_object_name = 'ads'              # Имя переменной в шаблоне
    
  def get_queryset(self):                 # Метод для получения данных
    return Advertisement.objects.filter(  # Возвращаем фильтрованный queryset
      category__slug=self.kwargs['category_slug'],  # Фильтр по slug категории
      status='published'                # И по статусу
    )
    
  def get_context_data(self, **kwargs):   # Добавляем данные в контекст
    context = super().get_context_data(**kwargs)  # Получаем базовый контекст
    context['category'] = get_object_or_404(  # Добавляем объект категории
      Category, slug=self.kwargs['category_slug']  # Ищем категорию по slug
    )
    return context                      # Возвращаем обновленный контекст  
    

class TagAdsListView(ListView):            # Класс для списка по тегу
  template_name = 'ads/pages/ad_tags.html'  # Шаблон для тегов
  context_object_name = 'ads'              # Имя переменной в шаблоне
    
  def get_queryset(self):                 # Метод получения данных
    return Advertisement.objects.filter(  # Фильтруем объявления
      tags__slug=self.kwargs['tag_slug'],  # По slug тега (ManyToMany)
      status='published'                # И по статусу
    )
    
  def get_context_data(self, **kwargs):   # Добавляем тег в контекст
    context = super().get_context_data(**kwargs)  # Базовый контекст
    context['tag'] = get_object_or_404(  # Добавляем объект тега
      Tag, slug=self.kwargs['tag_slug']  # Ищем тег по slug
    )
    return context                      # Возвращаем контекст
  
  
class AdDetailView(FavoriteMixin, DetailView):            # Класс для детального просмотра
    model = Advertisement                   #  Работаем с моделью Advertisement
    context_object_name = 'ad'              # Имя переменной в шаблоне
    template_name = 'ads/pages/ad_details.html'  # Шаблон деталей
    slug_field = 'slug'                    # Поле модели для поиска
    slug_url_kwarg = 'ad_slug'             # Имя параметра из URL
    
    def get_object(self, queryset=None):
      ad = super().get_object(queryset)
      
      user = self.request.user

      session_key = f'ad_{ad.id}_viewed' # "ad_32_viewed"
      if not self.request.session.get(session_key, False) and ad.owner != user:
        Advertisement.objects.filter(id=ad.id).update(views=F("views") + 1)
        ad.views = ad.views + 1
        self.request.session[session_key] = True
        
      if user.is_authenticated and user != ad.owner and not ad.viewed_users.filter(id=user.id).exists():
        ad.viewed_users.add(user)

      return ad
    
    
class AdCreateView(LoginRequiredMixin, CreateView):  # Требует авторизацию
  model = Advertisement                   # Модель для создания
  form_class = AdvertisementForm          # Кастомная форма
  template_name = 'ads/pages/ad_form.html'  # Шаблон формы
  
  def get_context_data(self, **kwargs):     # Добавляем заголовок и текст кнопки для создания
        context = super().get_context_data(**kwargs)
        context['title'] = "Создать объявление"
        context['submit_button_text'] = "Опубликовать"
        return context
    
  def form_valid(self, form):             # Вызывается при валидной форме
    ad = form.save(commit=False)        # Не сохраняем сразу в БД
    ad.owner = self.request.user        # Устанавливаем владельца
    ad.save()                           # Теперь сохраняем
    for tag_name in form.cleaned_data.get('tags_input', []):  # Обработка тегов
      tag, _ = Tag.objects.get_or_create(name=tag_name)  # Создаем/получаем тег
      ad.tags.add(tag)                # Добавляем тег к объявлению
    return super().form_valid(form)     # Вызываем родительский метод
    
  def get_success_url(self):              # Куда перенаправить после успеха
    return reverse_lazy('ads:ad_details', kwargs={'ad_slug': self.object.slug})  # На детали
  
  
class AdUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):  # Требует прав
  model = Advertisement                   # Модель
  form_class = AdvertisementForm          # Форма
  template_name = 'ads/pages/ad_form.html'  # Шаблон
  
  
  def get_context_data(self, **kwargs):     # Добавляем заголовок и текст кнопки для редактирования
        context = super().get_context_data(**kwargs)
        context['title'] = "Редактировать объявление"
        context['submit_button_text'] = "Сохранить"
        return context
    
  def test_func(self):                    # Проверка прав доступа
    return self.request.user == self.get_object().owner  # Только владелец

  def handle_no_permission(self):
    return render(self.request, 'ads/pages/not_allowed.html', status=403)
    
  def form_valid(self, form):             # При валидной форме
    ad = form.save()                    # Сохраняем изменения
    ad.tags.clear()                     # Удаляем старые теги
    for tag_name in form.cleaned_data.get('tags_input', []):  # Обработка тегов
      tag, _ = Tag.objects.get_or_create(name=tag_name)  # Создаем/получаем
      ad.tags.add(tag)                # Добавляем теги
    return super().form_valid(form)     # Стандартная логика
    
  def get_success_url(self):              # URL после успеха
    return reverse_lazy('ads:ad_details', kwargs={'ad_slug': self.object.slug})  # На детали
  
  
class AdDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):  # Для удаления
  model = Advertisement                   # Модель
  context_object_name = 'ad'              # Имя переменной в шаблоне
  template_name = 'ads/pages/confirm_ad_delete.html'  # Шаблон подтверждения
  success_url = reverse_lazy('ads:ad_list')  # Куда редиректить после удаления
    
  def test_func(self):                    # Проверка прав
    return self.request.user == self.get_object().owner  # Только владелец
  
  def handle_no_permission(self):
    return render(self.request, 'ads/pages/not_allowed.html', status=403)
  
  
class MainPageView(TemplateView):          # Просто отображает шаблон
  template_name = 'ads/pages/main_page.html'  # Указываем шаблон
  
  def get_context_data(self, **kwargs):
      context = super().get_context_data(**kwargs)
      context["categories"] = Category.objects.all()
      return context
    
  
@login_required
def toggle_favorite(request, ad_id):
    # Добавить/удалить из избранного
    ad = get_object_or_404(Advertisement, id=ad_id)
    # Проверяем, есть ли уже в избранном
    favorite = Favorite.objects.filter(user=request.user, ad=ad).first()
    
    if favorite:
        favorite.delete()  # удаляем
    else:
        Favorite.objects.create(user=request.user, ad=ad)  # добавляем
    
    return redirect(request.META.get('HTTP_REFERER', 'ads:ad_list'))
  
  
class MyFavoritesView(LoginRequiredMixin, FavoriteMixin, ListView):
    """Страница с избранными объявлениями пользователя"""
    template_name = 'ads/pages/ad_list.html'  # Используем тот же шаблон
    context_object_name = 'ads'
    paginate_by = 3
    
    def get_queryset(self):
        """Получаем только избранные объявления пользователя"""
        # Получаем ID избранных объявлений
        favorite_ids = self.request.user.favorites.values_list('ad_id', flat=True)
        
        # Возвращаем объявления, которые в избранном И опубликованы
        return Advertisement.objects.filter(
            id__in=favorite_ids,
            status='published'
        ).select_related('category', 'owner')  # Оптимизация запросов
    
    def get_context_data(self, **kwargs):
        """Добавляем заголовок страницы"""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Мои избранные объявления'
        context['is_favorites_page'] = True  # Флаг для шаблона
        return context      