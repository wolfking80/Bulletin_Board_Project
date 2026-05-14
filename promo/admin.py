from django.contrib import admin

from django.contrib import admin
from .models import Request, Service, Type, Review, Purchase

@admin.register(Type)
class PromoAdmin(admin.ModelAdmin):
    # Выводим название и слаг, который генерируется автоматически
    list_display = ('id', 'name', 'slug')
    search_fields = ('name',)


@admin.register(Service)
class PromoAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'duration', 'can_be_combined', 'is_exclusive')
    list_filter = ('can_be_combined', 'is_exclusive')
    search_fields = ('name', 'description')
    list_editable = ('price', 'can_be_combined', 'is_exclusive') # Позволяет менять флаги прямо из списка


@admin.register(Request)
class PromoRequestAdmin(admin.ModelAdmin):
    # Выводим все важные поля, включая объявление ad
    list_display = ('id', 'user', 'phone', 'service', 'type', 'ad', 'status', 'created_at')
    # фильтры справа для модератора, чтобы быстро находить "Не прочитано"
    list_filter = ('status', 'created_at', 'type', 'service')
    search_fields = ('user__username', 'phone', 'comment', 'ad__title')
    list_editable = ('status',) # Позволяет модератору менять статус обращения в один клик
    date_hierarchy = 'created_at'


@admin.register(Review)
class PromoReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'service', 'rating', 'status', 'created_at')
    list_filter = ('status', 'rating', 'created_at')
    search_fields = ('author__username', 'text', 'service__name')
    list_editable = ('status',)


@admin.register(Purchase)
class PromoPurchaseAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'service', 'ad', 'ever_used', 'is_available')
    list_filter = ('ever_used', 'is_available', 'service')
    search_fields = ('user__username', 'service__name', 'ad__title')
    list_editable = ('is_available', 'ever_used')

