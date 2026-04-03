# 💰 Money Tracker — Backend API

> REST API для управления личными финансами: счета, транзакции, бюджеты, цели и аналитика.

---

## 🚀 Стек технологий

- **Django 4.2**
- **Django REST Framework**
- **PostgreSQL**
- **JWT (Bearer)**
- **Celery + Redis**
- **drf-spectacular (OpenAPI)**

---

## ✨ Возможности

- 🔐 JWT-аутентификация
- 💳 Управление счетами
- 💸 Доходы и расходы
- 🏷️ Категории и теги
- 🔁 Регулярные транзакции
- 🎯 Финансовые цели
- 📊 Аналитика и отчёты
- 🚨 Уведомления о превышении бюджета
- ⚙️ Фоновые задачи (Celery)

---

## 📦 Быстрый старт

```bash
git clone "Ссылка на ваш репозиторий"
cd money-tracker-backend
python -m venv venv
venv\Scripts\activate   # или venv/bin/activate для Linux
pip install -r requirements.txt 
```

## ⚙️ Настройка
### База данных (PostgreSQL)

```SQL
-- Подключиться под суперпользователем postgres
psql -U postgres

-- Создать базу данных
CREATE DATABASE money_db;

-- Создать пользователя с паролем
CREATE USER money_user WITH PASSWORD 'secure_password';

-- Дать все права на базу данных
GRANT ALL PRIVILEGES ON DATABASE money_db TO money_user;
```
⚠️ Однако после этих действий пользователь money_user по умолчанию не имеет прав на создание таблиц внутри базы данных. Для этого нужно также выдать права на схему public (или создать отдельную схему):
```SQL
-- Подключиться к целевой базе данных
\c money_db;

-- Дать права на схему public
GRANT ALL ON SCHEMA public TO money_user;
GRANT ALL PRIVILEGES ON DATABASE money_db TO money_user;

-- Сделать пользователя владельцем базы данных (опционально)
ALTER DATABASE money_db OWNER TO money_user;
```
 Если вы используете pgAdmin, права выдаются через графический интерфейс:
- ПКМ по базе данных → Properties → Security → добавить пользователя → ALL.
- ПКМ по схеме public → Properties → Privileges → добавить пользователя → ALL.

⚠️ Без прав на схему public Django не сможет выполнить миграции и получит ошибку: нет доступа к схеме public.

В settings.py:
```Python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'money_db',
        'USER': 'money_user',
        'PASSWORD': 'secure_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```
---
## ▶️ Запуск 
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
📍 API: http://127.0.0.1:8000/

⚡ Celery (опционально)
```bash
celery -A money_tracker worker --loglevel=info
celery -A money_tracker beat --loglevel=info
```
---

## 📖 Документация API 
- Swagger: http://127.0.0.1:8000/api/schema/swagger-ui/
- ReDoc: http://127.0.0.1:8000/api/schema/redoc/

👉 Полное описание API:
API_REFERENCE.md

---

## 🔐 Аутентификация 
Используется JWT:
```bash
Authorization: Bearer <token>
```
📊 Пример использования
```bash
curl -X POST http://127.0.0.1:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"Qwerty123"}'
```

---

## 🧠 Архитектура (кратко)

| Компонент | Назначение |
|----------|-----------|
| Django Signals | Автоматическое обновление балансов при изменении транзакций |
| Celery | Фоновые задачи (регулярные транзакции, уведомления, проверки бюджетов) |
| Django REST Framework | Построение REST API |
| PostgreSQL | Хранение данных |

---

## ⚠️ 4. Возможные проблемы и решения

| Проблема | Решение |
|----------|--------|
| ModuleNotFoundError: No module named `pkg_resources` | Выполните `pip install setuptools` |
| Ошибка подключения к PostgreSQL | Проверьте, что служба PostgreSQL запущена; корректность логина/пароля в `settings.py` |
| `jwt_auth.views` не содержит нужных классов | В проекте используются `JSONWebToken` и `RefreshJSONWebToken` |
| Celery не запускается | Убедитесь, что запущен Redis; проверьте `CELERY_BROKER_URL` |
| 401 Unauthorized | Используйте `Bearer`, а не `JWT`; возможно, токен истёк |
| Ошибка миграций (`no such table`) | Выполните `python manage.py migrate --run-syncdb` или пересоздайте миграции |