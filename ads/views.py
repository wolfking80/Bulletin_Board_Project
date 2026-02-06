from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.contrib import messages

from django.db.models import F, Q, Avg, FloatField
from django.db.models.functions import Cast

from ads.models import Advertisement, Category, Tag, Favorite, SellerRating, AdQuestion
from ads.forms import AdvertisementForm
from .mixins import FavoriteMixin 


User = get_user_model()


# Вспомогательная универсальная функция
def get_ads_queryset(request):
  qs = Advertisement.objects.annotate(
        seller_rating=Avg(Cast('owner__received_ratings__is_positive', FloatField())) * 100
    ).filter(status='published')

# Проверка на "Избранное"
  is_fav_page = request.GET.get('is_fav') == '1' or 'my-favorites' in request.path
  if is_fav_page and request.user.is_authenticated:
    fav_ids = list(request.user.favorites.values_list('ad_id', flat=True))
    qs = qs.filter(id__in=fav_ids).exclude(owner=request.user).distinct()
  
# Получение параметров
  search = request.GET.get('search')
  search_category = request.GET.get('search_category')
  search_tag = request.GET.get('search_tag')
  min_price = request.GET.get('min_price')
  max_price = request.GET.get('max_price')
  min_rating = request.GET.get('min_rating')

# Расширенный поиск по тексту
  if search:
    query = Q(title__icontains=search) | Q(text__icontains=search)
    if search_category:
      query |= Q(category__name__icontains=search)
    if search_tag:
      query |= Q(tags__name__icontains=search)
    qs = qs.filter(query)

# Фильтры цен и рейтинга
  if min_price:
    qs = qs.filter(Q(price__gte=min_price) | Q(price__isnull=True))
  if max_price:
    qs = qs.filter(Q(price__lte=max_price) | Q(price__isnull=True))
  if min_rating:
    qs = qs.filter(Q(seller_rating__gte=min_rating) | Q(seller_rating__isnull=True))

  return qs.order_by('-created_at', '-id').distinct()


class AdsListView(FavoriteMixin, ListView):                # Создаем класс на основе ListView
  context_object_name = 'ads'              # Имя переменной в шаблоне
  template_name = 'ads/pages/ad_list.html' # Путь к шаблону
  ads_per_batch = 6
  
  def get_queryset(self):
    # Просто вызываем функцию и берем первые 6
    self.ads_query = get_ads_queryset(self.request)
    return self.ads_query[:self.ads_per_batch]
  
  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context["has_more_ads"] = self.ads_query.count() > self.ads_per_batch
    context["ads_per_batch"] = self.ads_per_batch
    return context
  
  
class AdSearchView(ListView):
  template_name = 'ads/pages/ad_search.html'
  context_object_name = 'ads'
  ads_per_batch = 6
  
  def get_queryset(self):
  # Вызываем универсальную функцию
    qs = get_ads_queryset(self.request)

  # Если юзер ничего не ввел, возвращаем пустой QuerySet
    params = ['search', 'min_price', 'max_price', 'min_rating']
    if not any(self.request.GET.get(p) for p in params):
      return Advertisement.objects.none()

    self.full_search_qs = qs.order_by(
      F('price').asc(nulls_last=True), 
      F('seller_rating').desc(nulls_last=True), 
      '-created_at',
      '-id'
    ).distinct()
    
    return self.full_search_qs[:self.ads_per_batch]

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    # Флаг: был ли запрос вообще
    context["search_performed"] = any(self.request.GET.values())
    if hasattr(self, 'full_search_qs'):
      context["has_more_ads"] = self.full_search_qs.count() > self.ads_per_batch
    context["ads_per_batch"] = self.ads_per_batch    
    return context
  
  
class CategoryAdsListView(FavoriteMixin, ListView):
  template_name = 'ads/pages/ads_category.html'
  context_object_name = 'ads'
  ads_per_batch = 6
    
  def get_queryset(self):
    #  Находим выбранную категорию по слагу
    self.category = get_object_or_404(Category, slug=self.kwargs['category_slug'])

    # Вызываем универсальную функцию (она найдет всё по сайту)
    qs = get_ads_queryset(self.request)

    # Ищем саму категорию ИЛИ тех, у кого этот объект является родителем (children)
    return qs.filter(
      Q(category=self.category) | Q(category__parent=self.category)
    ).order_by('-created_at', '-id')
    
  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    # Получение объекта категории для заголовка страницы
    context['category'] = get_object_or_404(
      Category, slug=self.kwargs['category_slug']
      )
    return context  
    

class TagAdsListView(FavoriteMixin, ListView):
  template_name = 'ads/pages/ad_tags.html'  # Шаблон для тегов
  context_object_name = 'ads'              # Имя переменной в шаблоне
  ads_per_batch = 6
    
  def get_queryset(self):
  # Получаем базовый набор данных (рейтинги, фильтры, поиск уже внутри)
    qs = get_ads_queryset(self.request)
        
  # Фильтруем по тегу из URL
  # Используем .distinct(), так как ManyToMany (теги) может дублировать строки
    return qs.filter(
      tags__slug=self.kwargs['tag_slug']
    ).order_by('-created_at', '-id').distinct()
    
  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
  # Передаем сам объект тега для заголовка страницы
    context['tag'] = get_object_or_404(
      Tag, slug=self.kwargs['tag_slug']
      )
    return context
  
  
class AdDetailView(FavoriteMixin, DetailView):            # Класс для детального просмотра
    model = Advertisement                   #  Работаем с моделью Advertisement
    context_object_name = 'ad'              # Имя переменной в шаблоне
    template_name = 'ads/pages/ad_details.html'  # Шаблон деталей
    slug_field = 'slug'                    # Поле модели для поиска
    slug_url_kwarg = 'ad_slug'             # Имя параметра из URL
    questions_per_batch = 2
    
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
      ad = self.get_object() # текущее объявление
      
    # Получаем 3 похожих объявления
      related_ads = Advertisement.objects.filter(  # фильтруем по категории
        category=self.object.category,             # та же категория, что и у просматриваемого
        status='published'                         # только опубликованные
      ).exclude(id=self.object.id).order_by('?')[:3]  # исключаем просматриваемое объявление из списка и выдаем 3 случайных
    
      context['related_ads'] = related_ads    # добавляем в контекст похожие объявления
      
      # Получаем все вопросы к этому объявлению
      questions_query = ad.questions.filter(parent__isnull=True).order_by('-created_at')
    
      # Передаем в шаблон только первую порцию
      context["questions"] = questions_query[:self.questions_per_batch]
      # Проверяем, нужно ли показывать кнопку "Загрузить еще"
      context["has_more_questions"] = questions_query.count() > self.questions_per_batch
      # Передаем размер порции, чтобы JS знал шаг смещения (offset)
      context["questions_per_batch"] = self.questions_per_batch        
    
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
  slug_url_kwarg = 'ad_slug'
  
  
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
  slug_url_kwarg = 'ad_slug'
    
  def test_func(self):                    # Проверка прав
    return self.request.user == self.get_object().owner  # Только владелец
  
  def handle_no_permission(self):
    return render(self.request, 'ads/pages/not_allowed.html', status=403)
  
  
class MainPageView(TemplateView):          # Просто отображает шаблон
  template_name = 'ads/pages/index.html'  # Указываем шаблон
  
  def get_context_data(self, **kwargs):
      context = super().get_context_data(**kwargs)
      context["categories"] = Category.objects.filter(parent__isnull=True)
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
    template_name = 'ads/pages/ad_list.html'  # Используем тот же шаблон
    context_object_name = 'ads'
    ads_per_batch = 6
    
    def get_queryset(self):
    # Вызываем ТУ ЖЕ функцию, она сама поймет, что это избранное по URL
      self.ads_query = get_ads_queryset(self.request)
      return self.ads_query[:self.ads_per_batch]

    def get_context_data(self, **kwargs):
      context = super().get_context_data(**kwargs)
      context['title'] = 'Мои избранные объявления'
      context['is_favorites_page'] = True
      context["has_more_ads"] = self.ads_query.count() > self.ads_per_batch
      context["ads_per_batch"] = self.ads_per_batch
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
  
  
def load_more_ads_view(request):
  import time
  time.sleep(1)
  offset = int(request.GET.get("offset", 0))
  limit = 6 
  
  ads_query = get_ads_queryset(request)
  
  # Если в запросе есть хоть один параметр поиска, 
  # заставляем API сортировать ТАК ЖЕ, как вьюшка поиска
  params = ['search', 'min_price', 'max_price', 'min_rating']
  if any(request.GET.get(p) for p in params):
    ads_query = ads_query.order_by(
      F('price').asc(nulls_last=True), 
      F('seller_rating').desc(nulls_last=True), 
      '-created_at','-id').distinct()
  else:
  # Для обычной главной страницы оставляем стандартную сортировку
    ads_query = ads_query.order_by('-created_at', '-id').distinct()
    
  total_count = ads_query.count()
        
  ads = list(ads_query[offset:offset + limit])
  
  fav_ids = []
  if request.user.is_authenticated:
    fav_ids = list(request.user.favorites.values_list('ad_id', flat=True))
  
  html = ''.join([render_to_string("ads/includes/ad_card.html", {"ad": ad, "favorite_ids": fav_ids}, request=request) for ad in ads])
    
  return JsonResponse({
    'html': html,
    'has_more': (offset + len(ads)) < total_count and len(ads) == limit
  })
  
  
@login_required
@require_POST
def add_question_view(request, ad_id):
  text = request.POST.get('text', '').strip()
  parent_id = request.POST.get('parent_id') # ID родителя
  if not text:
    return JsonResponse({'success': False, 'error': 'Текст вопроса не может быть пустым'})
    
  ad = get_object_or_404(Advertisement, id=ad_id)
  # данные для создания  
  question_data = {'ad': ad, 'author': request.user, 'text': text}
  # если пришел parent_id, находим родительский вопрос и привязываем его
  if parent_id:
    question_data['parent'] = get_object_or_404(AdQuestion, id=parent_id)
  # создаем запись (либо вопрос, либо ответ)      
  question = AdQuestion.objects.create(**question_data)
  # Рендерим кусочек HTML для вставки  
  question_html = render_to_string("ads/includes/question_container.html", 
                            {"question": question}, request=request)
    
  return JsonResponse({
    'success': True,
    'question_html': question_html,
    'questions_count': ad.questions.count()
}) 
  
  
def load_more_questions_view(request, ad_id):
  offset = int(request.GET.get("offset", 0))
  limit = 2
  import time
  time.sleep(1)

  ad = get_object_or_404(Advertisement, id=ad_id)
  questions_query = ad.questions.filter(parent__isnull=True).order_by('-created_at')
    
  questions = questions_query[offset : offset + limit]

  html = ''.join([
    render_to_string("ads/includes/question_container.html", {"question": q}, request=request)
    for q in questions
  ])
    
  has_more = offset + limit < questions_query.count()

  return JsonResponse({
    'html': html,
    'has_more': has_more
  })           