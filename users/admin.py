from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from users.models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
  # Что видим в таблице (списке)
  list_display = ('username', 'email', 'first_name', 'last_name', 'date_joined', 'avatar')
  # Что заполняем при СОЗДАНИИ нового юзера
  add_fieldsets = UserAdmin.add_fieldsets + (
    (None, {'fields': ('email', 'first_name', 'last_name', 'avatar')}),
  )
  # Поля при РЕДАКТИРОВАНИИ (внутри карточки)
  fieldsets = UserAdmin.fieldsets + (
        ('Дополнительная информация', {
            'fields': ('avatar',)
        }),
    )