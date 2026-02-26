from django.contrib import admin

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
    list_display = ('title', 'owner', 'status', 'created_at')
    list_filter = ('status', 'category')
    search_fields = ('title', 'text')
    # Добавляем инлайн в карточку объявления
    inlines = [AdPromotionInline]