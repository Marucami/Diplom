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
---
## ▶️ Запуск 
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
📍 API: http://127.0.0.1:8000/

---

👉 Полное описание API:
API_REFERENCE.md

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