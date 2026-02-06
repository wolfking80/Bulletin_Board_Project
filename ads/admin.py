from django.contrib import admin

from ads.models import Advertisement, Category, Tag


admin.site.register(Advertisement)
admin.site.register(Tag)

class CategoryInline(admin.TabularInline):
    model = Category
    fk_name = 'parent' # по какому полю связывать ( parent )
    extra = 2          # сколько пустых строк для новых подкатегорий показать сразу
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'slug')
    inlines = [CategoryInline]