# Запуск проекта

## Установка и настройка виртуального окружения
```bash
python -m venv venv
```
**Что делает:**
- Создает виртуальное окружение Python в папке `venv`. Это изолирует зависимости проекта от глобальных пакетов.

## Активация окружения
```bash
# Windows:
source venv/Scripts/activate
# Linux/Mac:
source venv/bin/activate
```
**Что делает:**  
- Активирует виртуальное окружение. После активации в терминале появится `(venv)`.

## Установка зависимостей
```bash
pip install -r requirements.txt
```
**Что делает:**  
- Устанавливает все пакеты из файла `requirements.txt` (Django и др.).

## Установка Pillow
```bash
pip install Pillow
```
**Что делает:** 
- Устанавливает библиотеку Pillow для обработки изображений

## Миграции базы данных
```bash
python manage.py makemigrations
python manage.py migrate
```
**Что делает:** 
- `makemigrations` - создаёт файлы миграций на основе моделей Django
- `migrate` - применяет миграции к базе данных

## Создание суперпользователя (опционально)
```bash
python manage.py createsuperuser
```
**Что делает:** 
- Создаёт администратора для доступа к панели Django (`/admin`).

## Установка phonenumbers и django-phonenumber-field
```bash
pip install phonenumbers
pip install django-phonenumber-field
```
**Что делает:** 
- Устанавливает пакеты  phonenumbers и django-phonenumber-field для работы с номерами телефонов

## Установка django-bootstrap5
```bash
pip install django-bootstrap5
```
**Что делает:** 
- Устанавливает пакет Django Bootstrap 5 — это интеграция фреймворка Bootstrap 5 с Django для удобной работы с фронтендом

- Настройка в settings.py:

INSTALLED_APPS = [
    ...
    'django_bootstrap5',
    ...
]

- В шаблоне:
{% load django_bootstrap5 %}

<!DOCTYPE html>
<html>
<head>
    {% bootstrap_css %}
    {% bootstrap_javascript %}
</head>
<body>
  ..............
</body>
</html>


## Django Shell Plus
Django Shell Plus - это расширенная интерактивная консоль Django с дополнительными возможностями:

```bash
# Запуск расширенной консоли с автоматическим импортом всех моделей
python manage.py shell_plus

# Запуск с выводом SQL-запросов для отладки
python manage.py shell_plus --print-sql
```

Преимущества shell_plus:
- Автоматический импорт всех моделей проекта
- Автоматический импорт основных модулей Django
- История команд и автодополнение
- Возможность просмотра генерируемых SQL-запросов
- Удобная среда для тестирования кода и работы


## Установка django-bootstrap-icons
```bash
pip install django-bootstrap-icons
```
**Что делает:** 
- Устанавливает пакет Bootstrap Icons — официальную библиотеку иконок для Bootstrap.

- Настройка в settings.py:

INSTALLED_APPS = [
    ...
   'django_bootstrap_icons',
    ...
]

- В шаблоне:
{% load bootstrap_icons %}

