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