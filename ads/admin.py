from django.contrib import admin
from django.db.models import Count

from ads.models import Advertisement, Category, Tag, AdPromotion

admin.site.register(Tag)

class CategoryInline(admin.TabularInline):
    model = Category
    fk_name = 'parent' # по какому полю связывать ( parent )
    extra = 2          # сколько пустых строк для новых подкатегорий показать сразу
    
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'slug')
    inlines = [CategoryInline]
    
    
# Создаем инлайн для продвижения
class AdPromotionInline(admin.StackedInline):
    model = AdPromotion
    can_delete = False
    verbose_name_plural = 'Услуги продвижения (VIP, Огонек, Цвет, ТОП)'
    # поля для отображения
    fields = ('is_vip', 'is_urgent', 'is_colored', 'is_top')
    
    # Регистрируем объявление с этим инлайном
@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'status', 'created_at', 'get_fav_count')
    list_filter = ('status', 'category')
    search_fields = ('title', 'text')
    # Добавляем инлайн в карточку объявления
    inlines = [AdPromotionInline]
    
    # Оптимизация запроса, чтобы админка не «висла» от большого количества Count-запросов
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(fav_count_attr=Count('favorited_by'))

    # Метод для вывода значения добавлений в Избранное
    @admin.display(description='★ Избранное', ordering='fav_count_attr')
    def get_fav_count(self, obj):
        return obj.fav_count_attr