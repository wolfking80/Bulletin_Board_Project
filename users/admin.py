from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from users.models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
  # Что видим в таблице (списке)
  list_display = ('username', 'email', 'first_name', 'last_name', 'date_joined', 'email_confirmed', 'notifications_enabled','avatar')
  # Добавляем фильтры
  list_filter = UserAdmin.list_filter + ('email_confirmed', 'notifications_enabled', 'selected_theme')
  # Поля для поиска
  search_fields = UserAdmin.search_fields + ('phone_number',)
  # Что заполняем при СОЗДАНИИ нового юзера
  add_fieldsets = UserAdmin.add_fieldsets + (
    (None, {'fields': ('email', 'first_name', 'last_name', 'email_confirmed', 'notifications_enabled', 'avatar')}),
  )
  # Поля при РЕДАКТИРОВАНИИ (внутри карточки)
  fieldsets = UserAdmin.fieldsets + (
        ('Дополнительная информация', {
            'fields': ('avatar',)
        }),
        ('Настройки уведомлений', {
            'fields': ('email_confirmed', 'notifications_enabled'),
            'description': 'Управление email уведомлениями и подтверждением'
        }),
    )