# 💰 Money Tracker API

Backend-сервис для приложения по учёту личных финансов.

Позволяет отслеживать доходы и расходы, управлять категориями и анализировать финансовое состояние пользователя.

---

## 🚀 Основные возможности

- 📊 Учёт доходов и расходов
- 🏷️ Категории с балансом
- 📈 Аналитика (доходы, расходы, баланс)
- 🎯 Прогноз достижения финансовой цели
- 🔍 Фильтрация транзакций по датам
- 🔐 Авторизация пользователей (сессии)

---

## 🧱 Технологии

- **Django 4.2**
- **Django REST Framework**
- **SQLite (встроенная база данных)**
- **Session Authentication (cookie-based)**

---

## 📁 Структура проекта

```bash
money_tracker/
├── api/
│ ├── models.py
│ ├── views.py
│ ├── serializers.py
│ ├── urls.py
│ └── services/
│        ├── finance_service.py
│        └── analytics_service.py
│
├── money_tracker/
│ ├── settings.py
│ ├── urls.py
│
├── frontend_build/
├── db.sqlite3
└── manage.py
```

---

## ⚙️ Установка и запуск

### 1. Клонировать репозиторий

```bash
git clone https://github.com/your-repo/money-tracker.git
cd money-tracker
```
### 2. Создать виртуальное окружение
```bash
python -m venv venv
source venv/bin/activate  # Linux / Mac
venv\Scripts\activate     # Windows
```
### 3. Установить зависимости
```bash
pip install -r requirements.txt
```
### 4. Применить миграции
```bash
python manage.py migrate
```
### 5. Запустить сервер
```bash
python manage.py runserver
```
---
## 🌐 API эндпоинты
## 🔐 Авторизация

| Метод | URL | Тело запроса | Ответ | Описание |
|------|-----|-------------|-------|----------|
| POST | `/api/register/` | `{ "username": "user", "password": "pass" }` | `{ "message": "User created" }` | Регистрация пользователя |
| POST | `/api/login/` | `{ "username": "user", "password": "pass" }` | `{ "message": "Logged in" }` | Вход в систему |
| POST | `/api/logout/` | — | `{ "message": "Logged out" }` | Выход из системы |

---

## 💰 Транзакции

| Метод | URL | Тело запроса | Ответ | Описание |
|------|-----|-------------|-------|----------|
| GET | `/api/transactions/` | — | `[]` | Получить список транзакций пользователя |
| POST | `/api/transactions/` | `{ "amount": 1000, "category_id": 1, "type": "income" }` | `{ ...transaction }` | Создать транзакцию |

---

## 🔍 Фильтрация транзакций

| Параметр | Тип | Описание |
|----------|-----|----------|
| start | string (YYYY-MM-DD) | Начальная дата |
| end | string (YYYY-MM-DD) | Конечная дата |

**Пример:**

```bash
/api/transactions/?start=2024-01-01&end=2024-12-31
```
---
## 🏷️ Категории

| Метод | URL | Тело запроса | Ответ | Описание |
|------|-----|-------------|-------|----------|
| GET | `/api/categories/` | — | `[]` | Получить список категорий |
| POST | `/api/categories/` | `{ "name": "Еда", "balance": 0 }` | `{ ...category }` | Создать категорию |

---

## 📊 Аналитика

| Метод | URL | Тело запроса | Ответ | Описание |
|------|-----|-------------|-------|----------|
| GET | `/api/analytics/` | — | `{ "income": 0, "expense": 0, "balance": 0 }` | Общая финансовая статистика |

---

## 🎯 Прогноз цели

| Метод | URL | Тело запроса | Ответ | Описание |
|------|-----|-------------|-------|----------|
| GET | `/api/forecast/?goal=10000` | — | `{ "months_to_reach": 6.5, ... }` | Прогноз достижения финансовой цели |

---

## 📌 Параметры прогноза

| Параметр | Тип | Описание |
|----------|-----|----------|
| goal | number | Сумма цели |
---

## 🔍 Фильтрация и поиск
### Фильтры
```bash 
?account=1&category=2&type=EX&date=2025-04-01
```
### Поиск
```bash 
?search=продукты
```
### Сортировка
```bash 
?ordering=-date
```
---
## ⚙️ Автоматические процессы
### Балансы
Обновляются автоматически через Django signals.

## 📌 Коды ответов

| Код | Значение |
|-----|---------|
| 200 | OK |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 404 | Not Found |
---

## Эндпоинты на будущее 
### 🔁 Повторяющиеся платежи

| Метод | URL |
|------|-----|
| GET | `/api/recurring/` |
| POST | `/api/recurring/` |
| PUT / PATCH | `/api/recurring/{id}/` |
| DELETE | `/api/recurring/{id}/` |

---

### 🎯 Цели

| Метод | URL |
|------|-----|
| GET | `/api/goals/` |
| POST | `/api/goals/` |
| PUT / PATCH | `/api/goals/{id}/` |
| DELETE | `/api/goals/{id}/` |

---

### 💰 Бюджеты

| Метод | URL |
|------|-----|
| GET | `/api/budgets/` |
| POST | `/api/budgets/` |
| PUT / PATCH | `/api/budgets/{id}/` |
| DELETE | `/api/budgets/{id}/` |

---

### 🔔 Уведомления

| Метод | URL |
|------|-----|
| GET | `/api/notifications/` |
| PATCH | `/api/notifications/{id}/` |
| DELETE | `/api/notifications/{id}/` |
---
## 📊 Аналитика
### Summary
GET /api/analytics/summary/

```json
{
  "total_income": 50000,
  "total_expense": 32000,
  "accounts_balance": 18000
}
```
### Другие endpoints 
- /api/analytics/by-period/
- /api/analytics/budgets-status/
- /api/analytics/compare/