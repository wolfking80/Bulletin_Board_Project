# Запуск проекта

## Установка и настройка виртуального окружения
```bash
python -m venv venv
```
**What it does:**
- Создает виртуальное окружение Python в папке `venv`. Это изолирует зависимости проекта от глобальных пакетов.

## Активация окружения
```bash
# Windows:
source venv/Scripts/activate
# Linux/Mac:
source venv/bin/activate
```
**What it does:**  
- Активирует виртуальное окружение. После активации в терминале появится `(venv)`.

## Установка зависимостей
```bash
pip install -r requirements.txt
```
**What it does:**  
- Устанавливает все пакеты из файла `requirements.txt` (Django и др.).

## Установка Pillow
```bash
pip install Pillow
```
**What it does:** 
- Устанавливает библиотеку Pillow для обработки изображений.

## Миграции базы данных
```bash
python manage.py makemigrations
python manage.py migrate
```
**What it does:** 
- `makemigrations` - создаёт файлы миграций на основе моделей Django.
- `migrate` - применяет миграции к базе данных.

## Создание суперпользователя (опционально)
```bash
python manage.py createsuperuser
```
**What it does:** 
- Создаёт администратора для доступа к панели Django (`/admin`).

## Установка phonenumbers и django-phonenumber-field
```bash
pip install phonenumbers
pip install django-phonenumber-field
```
**What it does:** 
- Устанавливает пакеты  phonenumbers и django-phonenumber-field для работы с номерами телефонов.

## Установка django-bootstrap5
```bash
pip install django-bootstrap5
```
**What it does:** 
- Устанавливает пакет Django Bootstrap 5 — это интеграция фреймворка Bootstrap 5 с Django для удобной работы с фронтендом.

- Настройка в settings.py:
```python
INSTALLED_APPS = [
    ...
    'django_bootstrap5',
    ...
]
```

- В шаблоне:
```html
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
```

## Django Shell Plus
Django Shell Plus - это расширенная интерактивная консоль Django с дополнительными возможностями:

```bash
# Запуск расширенной консоли с автоматическим импортом всех моделей
python manage.py shell_plus

# Запуск с выводом SQL-запросов для отладки
python manage.py shell_plus --print-sql
```
**Преимущества shell_plus:**
- Автоматический импорт всех моделей проекта.
- Автоматический импорт основных модулей Django.
- История команд и автодополнение.
- Возможность просмотра генерируемых SQL-запросов.
- Удобная среда для тестирования кода и работы.

## Установка django-bootstrap-icons
```bash
pip install django-bootstrap-icons
```
**What it does:** 
- Устанавливает пакет Bootstrap Icons — официальную библиотеку иконок для Bootstrap.

- Настройка в settings.py:
```python
INSTALLED_APPS = [
    ...
   'django_bootstrap_icons',
    ...
]
```

- В шаблоне:
```html
{% load bootstrap_icons %}
```

## Установка Unidecode
```bash
pip install Unidecode 
```
**What it does:**  
- Устанавливает библиотеку Unidecode для преобразования Unicode-текста в ASCII.
- Позволяет корректно обрабатывать символы разных языков (удаляет акценты, диакритические знаки).

## Установка django-widget-tweaks
```bash
pip install django-widget-tweaks
```
**What it does:**
- Устанавливает пакет django-widget-tweaks для кастомизации форм.
- Позволяет настраивать CSS-классы, плейсхолдеры и атрибуты полей ввода прямо внутри HTML-шаблонов.

- В шаблоне:
```html
{% load widget_tweaks %}
```

## Установка yookassa
```bash
pip install yookassa
```
**What it does:**
- Устанавливает официальный SDK ЮKassa.
- Интегрирует прием онлайн-платежей на сайте для оплаты тарифов продвижения и рекламы.

## Установка python-telegram-bot
```bash
pip install python-telegram-bot
```
**What it does:**
- Устанавливает библиотеку для работы с Telegram Bot API.
- Используется для реализации функций Telegram-бота внутри основного процесса Django.

## Установка psycopg2-binary
```bash
pip install psycopg2-binary
```
**What it does:**
- Устанавливает автономный адаптер базы данных PostgreSQL для Python.
- Необходим для подключения Django к контейнеру базы данных PostgreSQL.

## Установка python-dotenv
```bash
pip install python-dotenv
```
**What it does:**
- Устанавливает библиотеку для чтения переменных окружения из файла `.env`.
- Используется для безопасного хранения секретных ключей, доступов к БД, токенов бота и ЮKassa.

## Установка sqlparse
```bash
pip install sqlparse
```
**What it does:**
- Устанавливает парсер SQL-запросов.
- Используется пакетом `django-extensions` для красивого форматирования и подсветки SQL-кода при вызове команды `shell_plus --print-sql`.

## Установка httpx и requests
```bash
pip install httpx requests
```
**What it does:**
- Устанавливает HTTP-клиенты для отправки внешних сетевых запросов.
- Требуются для стабильной отправки запросов к API ЮKassa, Telegram и сторонним сервисам.

## Дополнительные системные зависимости
Следующие пакеты устанавливаются автоматически как обязательные зависимости для стабильной работы Django, асинхронного режима, сетевых протоколов и безопасности:
- `Django==5.2.8` — Основной веб-фреймворк проекта.
- `asgiref`, `anyio`, `h11`, `httpcore` — Пакеты для поддержки асинхронности (ASGI) и HTTP/1.1 протоколов.
- `certifi`, `urllib3`, `idna`, `charset-normalizer` — Пакеты для работы с SSL-сертификатами, безопасными сетевыми соединениями и кодировками.
- `defusedxml` — Защита парсеров XML от уязвимостей и атак.
- `netaddr` — Библиотека для валидации и работы с IP-адресами сетевых запросов.
- `tzdata` — Системная база данных часовых поясов.
- `sqlparse` — Форматирование SQL-запросов.
- `distro`, `Deprecated`, `wrapt` — Вспомогательные системные библиотеки для совместимости кода и версий.

---

## Развертывание проекта в Docker

### Настройка окружения
Перед запуском контейнеров создайте файл `.env` в корне проекта:
```env
DEBUG=True
SECRET_KEY=your_secret_key_here
ALLOWED_HOSTS=localhost,127.0.0.1,.ngrok-free.app
DB_NAME=billboard_db
DB_USER=postgres
DB_PASSWORD=secret_password
TELEGRAM_BOT_TOKEN=your_bot_token_here
YOOKASSA_SHOP_ID=your_shop_id
YOOKASSA_SECRET_KEY=your_yookassa_key
```

### Сборка и запуск контейнеров
```bash
docker compose up -d --build
```
**What it does:**
- Собирает Docker-образы и запускает контейнер приложения `ads_app_dev` (порт 8001) и базы данных PostgreSQL `ads_db` (порт 5433).

### Выполнение команд внутри Docker-контейнера
Поскольку проект упакован в Docker, все команды Django выполняются через утилиту `docker compose exec app`:

```bash
# Выполнение миграций:
docker compose exec app python manage.py makemigrations
docker compose exec app python manage.py migrate

# Создание суперпользователя:
docker compose exec app python manage.py createsuperuser

# Запуск расширенной интерактивной консоли Django Shell Plus:
docker compose exec app python manage.py shell_plus --print-sql
```

## Тестирование платежей ЮKassa (Локально)
Для тестирования входящих уведомлений (Webhooks) от ЮKassa на локальной машине используется утилита `ngrok`.

```bash
ngrok http 8001
```
**What it does:**
- Создает временный публичный домен, который перенаправляет трафик на порт вашего контейнера. Полученный адрес необходимо указать в личном кабинете ЮKassa для получения вебхуков.

## Деплой на боевой сервер (billboardshop.ru)
На сервере проект работает по схеме: Внешний Nginx -> Gunicorn (внутри Docker-контейнера) -> Django.

```bash
# 1. Сборка статических файлов на сервере
docker compose exec app python manage.py collectstatic --no-input

# 2. Перезапуск контейнеров после обновлений кода
docker compose up -d --build

# 3. Перезапуск веб-сервера Nginx на хосте (при изменении конфигов)
sudo systemctl restart nginx
```
**What it does:**
- `collectstatic` собирает всю статику проекта в единую директорию для раздачи через Nginx. Команды docker перезапускают контейнеры на продакшене.
