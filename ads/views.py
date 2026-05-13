import random
from django.db import transaction

from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse, reverse_lazy
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.contrib.auth import get_user_model

from django.db.models import F, Q, Avg, Count

from ads.models import Advertisement, Category, Tag, Favorite, SellerRating, AdQuestion
from ads.forms import AdvertisementForm
from .mixins import FavoriteMixin, OwnerRequiredMixin 


User = get_user_model()

# Вспомогательная универсальная функция
def get_ads_queryset(request):
    # Инициализация базового набора данных с оптимизацией
    qs = Advertisement.objects.select_related('promotion', 'category', 'owner').with_metrics()

    # Фильтрация по статусу и владельцу
    owner_id = request.GET.get('owner_id')
    show_all = request.GET.get('show_all') in ['True', '1']
    
    if owner_id:
        qs = qs.filter(owner_id=owner_id)
    
    if not show_all:
        qs = qs.filter(status='published')

    # Избранное
    is_fav_page = request.GET.get('is_fav') == '1' or 'my-favorites' in request.path
    if is_fav_page and request.user.is_authenticated:
        qs = qs.filter(favorited_by__user=request.user).exclude(owner=request.user)

    category_param = request.GET.get('category')
    if category_param and category_param != 'None':
    # Проверяем, что нам пришло: число (ID) или строка (слаг)
      if category_param.isdigit():
        # Если это число (старая логика), ищем по ID
        selected_cat = Category.objects.filter(id=int(category_param)).first()
      else:
        # Если это строка (наш новый слаг 'nedvizhimost'), ищем сразу по слагу
        selected_cat = Category.objects.filter(slug=category_param).first()

      if selected_cat:
        # Ищем саму категорию и всех её потомков через иерархию слагов
        qs = qs.filter(category__slug__startswith=selected_cat.slug)

    # Поиск и фильтры
    search_query = request.GET.get('search')
    qs = qs.search(
        search_query, 
        search_category=request.GET.get('search_category'),
        search_tag=request.GET.get('search_tag')
    ).apply_filters(
        min_price=request.GET.get('min_price'),
        max_price=request.GET.get('max_price'),
        min_rating=request.GET.get('min_rating')
    )

    # Сортировка
    is_searching = any(request.GET.get(p) for p in ['search', 'min_price', 'max_price', 'min_rating'])
    return qs.smart_order(is_search=is_searching)


class BaseAdListView(FavoriteMixin, ListView):
    context_object_name = 'ads'
    ads_per_batch = 6

    def get_queryset(self):
        # Берем базовый набор данных
        qs = get_ads_queryset(self.request).with_metrics()
        
        # Даем возможность дочерним классам добавить свои фильтры (поиск, категории и т.д.)
        qs = self.filter_queryset(qs)
        
        # Применяем сортировку к ПОЛНОМУ отфильтрованному набору
        self.full_queryset = qs.smart_order(is_search=self.is_search_mode())
        
        # И только теперь делаем срез для первой страницы
        return self.full_queryset[:self.ads_per_batch]

    def filter_queryset(self, qs):
        # По умолчанию ничего не фильтруем, переопределим в детях
        return qs

    def is_search_mode(self):
        # Флаг для smart_order, по умолчанию False
        return False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["has_more_ads"] = self.full_queryset.count() > self.ads_per_batch
        context["ads_per_batch"] = self.ads_per_batch
        return context

class AdsListView(BaseAdListView):
    template_name = 'ads/pages/ad_list.html'

    def get_queryset(self):
        return super().get_queryset()[:self.ads_per_batch]

class AdSearchView(BaseAdListView):
    template_name = 'ads/pages/ad_search.html'

    def is_search_mode(self):
        return True

    def filter_queryset(self, qs):
        query = self.request.GET.get('search')
        
        # Если параметров поиска нет, возвращаем пустоту
        if not any([query, self.request.GET.get('min_price'), self.request.GET.get('min_rating')]):
            return qs.none()

        # Применяем поиск и фильтры К ЦЕЛОМУ КВЕРИСЕТУ
        qs = qs.search(
            query, 
            search_category=self.request.GET.get('search_category') == 'on',
            search_tag=self.request.GET.get('search_tag') == 'on'
        ).apply_filters(
            min_price=self.request.GET.get('min_price'),
            max_price=self.request.GET.get('max_price'),
            min_rating=self.request.GET.get('min_rating')
        )
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Флаг для шаблона, чтобы понимать, показывать ли результаты или надпись "Введите запрос"
        query_params = ['search', 'min_price', 'min_rating']
        context['search_performed'] = any(self.request.GET.get(p) for p in query_params)
        return context

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Флаг, что поиск был запущен
        context['search_performed'] = any(self.request.GET.values())
        return context


class CategoryAdsListView(BaseAdListView):
    template_name = 'ads/pages/ads_category.html'

    def filter_queryset(self, qs):
        # Находим категорию по слагу из URL
        self.category = get_object_or_404(Category, slug=self.kwargs['category_slug'])
        # Фильтруем по дереву слагов 
        return qs.filter(category__slug__startswith=self.category.slug)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        context['title'] = f"Категория: {self.category.name}"
        return context
  

class TagAdsListView(BaseAdListView):
    template_name = 'ads/pages/ad_tags.html'

    def filter_queryset(self, qs):
        # Сохраняем слаг тега в атрибут класса, чтобы он был доступен везде
        self.tag_slug = self.kwargs.get('tag_slug')
        return qs.filter(tags__slug=self.tag_slug)

    def get_context_data(self, **kwargs):
        # Вызываем родительский метод
        context = super().get_context_data(**kwargs)
        
        # Ищем объект тега в базе по слагу
        tag_obj = Tag.objects.filter(slug=self.tag_slug).first()
        
        # Если нашли — берем красивое имя (name), если нет — используем слаг из URL
        tag_name = tag_obj.name if tag_obj else self.tag_slug
        
        # Формируем итоговый заголовок
        context['title'] = f"Объявления с тегом: #{tag_name}"
        return context


class AdDetailView(FavoriteMixin, DetailView):
    model = Advertisement
    context_object_name = 'ad'
    template_name = 'ads/pages/ad_details.html'
    slug_url_kwarg = 'ad_slug'
    questions_per_batch = 2

    def get_object(self, queryset=None):
        # Добавляем select_related, чтобы не дергать базу ради владельца или категории в шаблоне
        if queryset is None:
            queryset = self.get_queryset()
        
        ad = super().get_object(queryset.select_related('owner', 'category'))
        self._update_views(ad)
        return ad

    def _update_views(self, ad):
        """Логика инкремента просмотров вынесена в отдельный метод"""
        session_key = f'ad_v_{ad.id}'
        if not self.request.session.get(session_key):
            # Атомарный апдейт в базе
            Advertisement.objects.filter(pk=ad.pk).update(views=F("views") + 1)
            ad.views += 1 # Обновляем объект в памяти для текущего рендера
            self.request.session[session_key] = True

            # Учет авторизованных уникальных просмотров
            user = self.request.user
            if user.is_authenticated and user != ad.owner:
                # Используем .add(), Django сам проверит уникальность, если есть Unique Together
                ad.viewed_users.add(user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ad = self.object
        
        # Оптимизация 'Похожие объявления' (без order_by('?'))
        # Берем последние 10 из категории и выбираем 3 случайных в Python
        related_qs = Advertisement.objects.filter(
            category=ad.category, status='published'
        ).exclude(id=ad.id).order_by('-created_at')[:10]
        context['related_ads'] = random.sample(list(related_qs), min(len(related_qs), 3))

        # Вопросы (используем префетч для ответов, если они будут нужны)
        questions_query = ad.questions.filter(parent__isnull=True).select_related('author')
        context.update({
            "questions": questions_query[:self.questions_per_batch],
            "has_more_questions": questions_query.count() > self.questions_per_batch,
            "questions_per_batch": self.questions_per_batch
        })
        return context


class BaseAdEditView(LoginRequiredMixin, SuccessMessageMixin):
    model = Advertisement
    form_class = AdvertisementForm
    template_name = 'ads/pages/ad_form.html'

    def form_valid(self, form):
        with transaction.atomic(): # Оборачиваем в транзакцию
            if not form.instance.pk:
                form.instance.owner = self.request.user
            
            self.object = form.save()
            
            # Оптимизация работы с тегами
            tags_names = form.cleaned_data.get('tags_input', [])
            if tags_names:
              tag_objects = []
              for name in tags_names:
                name = name.lower().strip()
                if not name: continue
                
                # get_or_create сразу сохраняет объект в базу, если его нет
                tag, created = Tag.objects.get_or_create(name=name)
                tag_objects.append(tag)
            
              self.object.tags.set(tag_objects)
        
        return super().form_valid(form)


    def get_success_url(self):
    # self.object — это только что сохраненное объявление
      return reverse('ads:ad_details', kwargs={'ad_slug': self.object.slug})

      

class AdCreateView(BaseAdEditView, CreateView):
    # Используем extra_context для простых строк вместо переопределения метода
    extra_context = {
        'title': "Создать объявление", 
        'submit_button_text': "Опубликовать"
    }

    def get_success_message(self, cleaned_data):
        return "Объявление успешно создано!"

class AdUpdateView(OwnerRequiredMixin, BaseAdEditView, UpdateView):
    extra_context = {
        'title': "Редактировать", 
        'submit_button_text': "Сохранить"
    }
    slug_url_kwarg = 'ad_slug'
    
    def form_valid(self, form):
        ad = form.save(commit=False)
        
        # Список полей, изменение которых требует повторной проверки
        critical_fields = ['title', 'text', 'price', 'category', 'goods_image']
        
        # Если пользователь поменял хотя бы одно критическое поле — сбрасываем статус
        if any(field in form.changed_data for field in critical_fields):
            ad.status = 'under_review'
            
        ad.save()
        form.save_m2m()
        return super().form_valid(form)

    def get_success_message(self, cleaned_data):
        return "Изменения сохранены!"
      

class AdDeleteView(LoginRequiredMixin, OwnerRequiredMixin, DeleteView):
    model = Advertisement
    template_name = 'ads/pages/confirm_ad_delete.html'
    success_url = reverse_lazy('ads:ad_list')
    slug_url_kwarg = 'ad_slug'
    

class MainPageView(TemplateView):
    template_name = 'ads/pages/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Подгружаем категории вместе с количеством объявлений
        context["categories"] = Category.objects.filter(parent__isnull=True).with_ad_count()
        return context
      

@login_required
@require_POST
def toggle_favorite(request, ad_id):
    ad = get_object_or_404(Advertisement, id=ad_id)
    # Используем get_or_create: если объект есть — удаляем, если нет — он создастся
    favorite, created = Favorite.objects.get_or_create(user=request.user, ad=ad)
    
    if not created:
        favorite.delete()
        is_favorite = False
    else:
        is_favorite = True

    return JsonResponse({
        'is_favorite': is_favorite,
        'fav_count': ad.favorited_by.count() # Здесь count оправдан, так как это точечный JSON-ответ
    })

class MyFavoritesView(BaseAdListView):
    template_name = 'ads/pages/ad_list.html'

    def filter_queryset(self, qs):
        # Базовая функция get_ads_queryset уже умеет находить избранное,
        # если в URL есть 'my-favorites'. Но для надежности 
        # (если URL изменится) лучше явно отфильтровать здесь:
        return qs.filter(favorited_by__user=self.request.user).exclude(owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': 'Мои избранные объявления',
            'is_favorites_page': True
        })
        return context
     
      
@login_required
@require_POST
def rate_seller(request, seller_id):
    seller = get_object_or_404(User, id=seller_id)
    score = int(request.POST.get('score', 0))

    if request.user == seller:
        return JsonResponse({'error': 'Self-rating not allowed'}, status=400)
    if score not in range(1, 6):
        return JsonResponse({'error': 'Invalid score'}, status=400)

    # Создаем или обновляем оценку
    rating, created = SellerRating.objects.update_or_create(
        voter=request.user, 
        seller=seller,
        defaults={'score': score}
    )

    # Считаем среднее и количество голосов
    stats = seller.received_ratings.aggregate(
        avg_rating=Avg('score'),
        total_votes=Count('id')
    )

    return JsonResponse({
        'avg_rating': round(stats['avg_rating'], 1) if stats['avg_rating'] else 0,
        'total_votes': stats['total_votes'],
        'user_score': score
    })

def load_more_ads_view(request):
    """AJAX подгрузка объявлений"""
    offset = int(request.GET.get("offset", 0))
    limit = 6
    
    # Используем оптимизированную функцию
    qs = get_ads_queryset(request).with_metrics()
    
    # Проверяем, передал ли JS-лоадер слаг текущей категории в GET-параметрах
    category_slug = request.GET.get('category')
    if category_slug and category_slug != 'None':
        # Фильтруем по иерархии слагов (включая все подкатегории)
        qs = qs.filter(category__slug__startswith=category_slug)
        
    # Считаем ОБЩЕЕ количество доступных объявлений строго в этой ветке
    total_count = qs.count()
    
    # Сортируем ПОЛНЫЙ отфильтрованный набор и берем нужную пачку (срез)
    ads = qs.smart_order()[offset : offset + limit]
    
    # Отрезаем ровно столько, сколько нужно для проверки "есть ли еще"
    # (делаем срез на 1 больше лимита, чтобы понять, есть ли следующая страница без .count())
    has_more = (offset + limit) < total_count

    # Подгружаем избранное для авторизованного пользователя
    fav_ids = []
    if request.user.is_authenticated:
        fav_ids = list(request.user.favorites.values_list('ad_id', flat=True))

    # Генерируем HTML каждой карточки и склеиваем их
    html = "".join([
        render_to_string("ads/includes/ad_card.html", {
            "ad": ad, 
            "favorite_ids": fav_ids,
            "request": request # Важно для проверки владельца внутри карточки
        }, request=request)
        for ad in ads
    ])

    return JsonResponse({
        'html': html,
        'has_more': has_more
    })

@login_required
@require_POST
def add_question_view(request, ad_id):
    text = request.POST.get('text', '').strip()
    if not text or len(text) < 2:
        return JsonResponse({'success': False, 'error': 'Слишком короткий текст'})

    ad = get_object_or_404(Advertisement, id=ad_id)
    parent_id = request.POST.get('parent_id')
    
    parent = get_object_or_404(AdQuestion, id=parent_id) if parent_id else None
    
    question = AdQuestion.objects.create(
        ad=ad, author=request.user, text=text, parent=parent
    )

    html = render_to_string("ads/includes/question_container.html", {
        "question": question
    }, request=request)

    return JsonResponse({
        'success': True,
        'question_html': html,
        'questions_count': ad.questions.count()
    })
    
    
def load_more_questions_view(request, ad_id):
    offset = int(request.GET.get("offset", 0))
    limit = 2
    ad = get_object_or_404(Advertisement, id=ad_id)
    
    # Берем только основные вопросы (не ответы)
    questions_query = ad.questions.filter(parent__isnull=True).order_by('-created_at')
    questions = questions_query[offset : offset + limit]
    
    # Рендерим каждый вопрос отдельно и склеиваем в одну строку
    html = ''.join([
        render_to_string("ads/includes/question_container.html", {"question": q}, request=request)
        for q in questions
    ])
    
    has_more = offset + limit < questions_query.count()
    return JsonResponse({
        'html': html,
        'has_more': has_more
    })          