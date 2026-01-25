from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.contrib import messages

from django.db.models import F, Q, Avg, FloatField
from django.db.models.functions import Cast

from ads.models import Advertisement, Category, Tag, Favorite, SellerRating
from ads.forms import AdvertisementForm
from .mixins import FavoriteMixin 


User = get_user_model()


class AdsListView(FavoriteMixin, ListView):                # Создаем класс на основе ListView
  model = Advertisement                    # Указываем модель для работы
  context_object_name = 'ads'              # Имя переменной в шаблоне
  template_name = 'ads/pages/ad_list.html' # Путь к шаблону
  queryset = Advertisement.objects.filter(status="published").order_by('created_at')  # Фильтрация
  paginate_by = 3                    # Пагинация - максимум 3 объявления на странице
  
  
class AdSearchView(ListView):
  template_name = 'ads/pages/ad_search.html'   # Путь к шаблону
  context_object_name = 'ads'                  # Имя переменной в шаблоне
  paginate_by = 3                              # Пагинация - максимум 3 объявления на странице
  
  def get_context_data(self, **kwargs):         # переопределяем метод, который готовит данные (контекст) для отправки в HTML
      context = super().get_context_data(**kwargs)   # метод родителя, чтобы не потерять стандартные данные
      context["search_performed"] = any(self.request.GET.keys())   # создаем флаг: если в URL есть хоть один GET-параметр (ключ), значит поиск был запущен
      return context                              # возвращаем готовый пакет данных
    
  
  def get_queryset(self):                      # основной метод, определяющий, какие именно записи из БД нужно достать
  # Аннотируем каждое объявление рейтингом продавца (0-100%)
    queryset = Advertisement.objects.annotate(
    seller_rating=
      Avg(Cast('owner__received_ratings__is_positive', FloatField())) * 100).filter(status='published')

  # Получаем данные из URL
    search_query = self.request.GET.get('search')    # вытаскиваем из адреса значение параметра search (то, что пользователь ввел в строку поиска)
    search_category = self.request.GET.get('search_category')   # проверяем, стоит ли галочка «искать в категориях»
    search_tag = self.request.GET.get('search_tag')             # проверяем, стоит ли галочка «искать в тэгах»
    min_price = self.request.GET.get('min_price')               # проверяем, указана ли мин. цена
    max_price = self.request.GET.get('max_price')               # проверяем, указана ли макс. цена
    min_rating = self.request.GET.get('min_rating')             # проверяем, указан ли мин. рейтинг продавца

  # Фильтруем по тексту
    if search_query:            # создаем Q-объект для поиска подстроки (icontains — без учета регистра) в заголовке ИЛИ в тексте объявления
      query = Q(title__icontains=search_query) | Q(text__icontains=search_query)
      if search_category:                                       # если галочка категорий активна..
        query |= Q(category__name__icontains=search_query)      # добавляем еще одно ИЛИ: искать совпадение в названии категории
      if search_tag:                                            # если галочка тэга активна..
        query |= Q(tags__name__icontains=search_query)          # добавляем еще одно ИЛИ: искать совпадение в названии тэга
      queryset = queryset.filter(query)

  # Фильтруем по цене, НЕ удаляя объявления без указания цены
    if min_price:
      queryset = queryset.filter(Q(price__gte=min_price) | Q(price__isnull=True))  # цена больше или равна значению ИЛИ цена не указана
    if max_price:
      queryset = queryset.filter(Q(price__lte=max_price) | Q(price__isnull=True))  # цена меньше или равна значению ИЛИ цена не указана

  # Фильтруем по рейтингу
    if min_rating:
      queryset = queryset.filter(Q(seller_rating__gte=min_rating) | Q(seller_rating__isnull=True))

  # Если ничего не введено — возвращаем пустой список
    if not any([search_query, min_price, max_price, min_rating]):
      return Advertisement.objects.none()

  # Сортировка: сначала те, где есть цена, внутри них — самые новые. 
  # Объявления "цена не указана" будут в самом низу.
  # Объявления продавцов без рейтинга (нулевым) ТОЖЕ будут видны
    return queryset.order_by(F('price').asc(nulls_last=True), F('seller_rating').desc(nulls_last=True), '-created_at').distinct()
  
class CategoryAdsListView(FavoriteMixin, ListView):        # Класс для списка по категории
  template_name = 'ads/pages/ads_category.html'  # Шаблон для категории
  context_object_name = 'ads'              # Имя переменной в шаблоне
  paginate_by = 3
    
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
  paginate_by = 3
    
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
      ad = super().get_object(queryset)      # получаем само объявление из базы
      
      user = self.request.user              # запоминаем, кто сейчас открыл страницу (авторизованный юзер или гость)

      session_key = f'ad_{ad.id}_viewed' # создаем уникальный ключ для текущего браузера (например, "ad_32_viewed")
      if not self.request.session.get(session_key, False) and ad.owner != user:  # если в сессии нет этого ключа (человек зашел впервые) И этот человек не является владельцем
        Advertisement.objects.filter(id=ad.id).update(views=F("views") + 1)  # запрос в БД: « + 1 к просмотрам». F-выражение нужно, чтобы избежать проблем, если два человека нажмут кнопку одновременно
        ad.views = ad.views + 1      # обновляем цифру в текущей переменной, чтобы на странице сразу отобразилось актуальное число
        self.request.session[session_key] = True   # записываем в сессию (куки браузера) флаг: «этот пользователь это объявление уже видел»
        
      if user.is_authenticated and user != ad.owner and not ad.viewed_users.filter(id=user.id).exists(): # проверка: юзер вошел в аккаунт И он не автор И его еще нет в списке «кто смотрел» в БД
        ad.viewed_users.add(user)   # добавляем связь между пользователем и объявлением в специальную таблицу

      return ad                     # возвращаем полностью обработанное объявление в шаблон
    
    def get_context_data(self, **kwargs):
      context = super().get_context_data(**kwargs)
    # Получаем 3 похожих объявления
      related_ads = Advertisement.objects.filter(  # фильтруем по категории
        category=self.object.category,             # та же категория, что и у просматриваемого
        status='published'                         # только опубликованные
      ).exclude(id=self.object.id).order_by('?')[:3]  # исключаем просматриваемое объявление из списка и выдаем 3 случайных
    
      context['related_ads'] = related_ads    # добавляем в контекст похожие объявления        
    
      if self.request.user.is_authenticated:
        context['favorite_ids'] = self.request.user.favorites.values_list('ad_id', flat=True) # для корректного отображения отметки "избранных" объявлений
        
      return context
    
    
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
    messages.success(self.request, 'Объявление успешно создано!')  
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
  template_name = 'ads/pages/index.html'  # Указываем шаблон
  
  def get_context_data(self, **kwargs):
      context = super().get_context_data(**kwargs)
      context["categories"] = Category.objects.all()
      return context
    
  
@login_required
@require_POST
def toggle_favorite(request, ad_id):
    # Добавить/удалить из избранного
    ad = get_object_or_404(Advertisement, id=ad_id)
    # Проверяем, есть ли уже в избранном
    favorite = Favorite.objects.filter(user=request.user, ad=ad).first()
    
    if favorite:
        favorite.delete()  # удаляем
        is_favorite = False
    else:
        Favorite.objects.create(user=request.user, ad=ad)  # добавляем
        is_favorite = True
    
    return JsonResponse({'is_favorite': is_favorite})
  
  
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
      
      
@login_required
@require_POST         # разрешает только POST-запросы. Это защита: нельзя изменить рейтинг, просто перейдя по ссылке.
def rate_seller(request, seller_id, rating_type):  # принимаем запрос, ID продавца и тип клика (plus или minus)
  seller = get_object_or_404(User, id=seller_id)   # ищем продавца в базе. Если такого ID нет, выдаст ошибку 404
  if request.user == seller:                       # проверка на «самолайк». Если ID текущего юзера совпадает с ID продавца, возвращаем ошибку 400
    return JsonResponse({'error': 'Self-rating not allowed'}, status=400)

  is_positive = (rating_type == 'plus')      # превращаем строку из URL в булево значение (True, если нажали плюс)
  rating = SellerRating.objects.filter(voter=request.user, seller=seller).first()  # ищем в базе, голосовал ли этот юзер за этого продавца ранее
    
  user_choice = 'none' # статус для JS, какую кнопку закрасить в итоге
    
  if rating:            # если голос уже существует
    if rating.is_positive == is_positive:  # если нажали ту же кнопку, что и раньше, то удаляем голос
      rating.delete()
    else:
      rating.is_positive = is_positive     # если нажали противоположную кнопку, то меняем значение в базеs
      rating.save()
      user_choice = rating_type # ставим статус plus или minu
  else:                         # если голоса еще не было, просто создаем новую запись SellerRating и ставим статус
    SellerRating.objects.create(voter=request.user, seller=seller, is_positive=is_positive)
    user_choice = rating_type
    
  pos = seller.received_ratings.filter(is_positive=True).count()   # считаем общее количество «пальцев вверх» у продавца
  neg = seller.received_ratings.filter(is_positive=False).count()  # считаем количество «пальцев вниз»
  total = pos + neg                                                # общее число проголосовавших
    
  # Считаем процент (защита от деления на ноль)
  trust_percent = round((pos / total) * 100) if total > 0 else 0

  return JsonResponse({         # упаковываем все новые цифры и статус user_choice в JSON-пакет и отправляем обратно в JS
    'pos': pos,
    'neg': neg,
    'trust_percent': trust_percent,
    'user_choice': user_choice
  })            