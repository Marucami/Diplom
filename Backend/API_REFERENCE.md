
---

# 📚 API_REFERENCE.md (подробная документация)

## 📍 Где искать документацию по API
После запуска бэкенда:
- http://127.0.0.1:8000/api/schema/swagger-ui/ – интерактивная документация.
- http://127.0.0.1:8000/api/schema/redoc/ – альтернативный вид.

Там описаны все эндпоинты, ожидаемые форматы, коды ответов. 


---

## 🔐 Аутентификация

### Регистрация

**POST** `/api/register/`
- Windows(cmd)
```json
curl -X POST http://127.0.0.1:8000/api/register/ -H "Content-Type: application/json" -d "{\"username\":\"alice\",\"password\":\"StrongP@ssw0rd\",\"password2\":\"StrongP@ssw0rd\",\"email\":\"alice@example.com\"}"
```
- Linux / macOS (bash)
```json
curl -X POST http://127.0.0.1:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"StrongP@ssw0rd","password2":"StrongP@ssw0rd","email":"alice@example.com"}'
```

### Логин(JWT)
POST /api/login/
- Для Windows (cmd)
```json
curl -X POST http://127.0.0.1:8000/api/login/ -H "Content-Type: application/json" -d "{\"username\":\"alice\",\"password\":\"StrongP@ssw0rd\"}"
```
- Linux / macOS (bash)
```json
curl -X POST http://127.0.0.1:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"StrongP@ssw0rd"}'

```
Сам токен берёте из ответа в консоли уже после регистрации и логина.\
Общий вид ответа:
```json
{
  "token_type": "Bearer",
  "token": "...",
  "expires_in": 300
}
```
## 📡 Основные ресурсы

### 💳 Accounts

| Метод | URL |
|------|-----|
| GET | `/api/accounts/` |
| POST | `/api/accounts/` |
| PUT / PATCH | `/api/accounts/{id}/` |
| DELETE | `/api/accounts/{id}/` |

**Пример:**

```json
{
  "name": "Наличные",
  "currency": "RUB"
}
```
---
### 💸 Transactions

| Метод | URL |
|------|-----|
| GET | `/api/transactions/` |
| POST | `/api/transactions/` |
| PUT / PATCH | `/api/transactions/{id}/` |
| DELETE | `/api/transactions/{id}/` |
---
### 🏷️ Categories

| Метод | URL |
|------|-----|
| GET | `/api/categories/` |
| POST | `/api/categories/` |
| PUT / PATCH | `/api/categories/{id}/` |
| DELETE | `/api/categories/{id}/` |

---

### 🔖 Tags

| Метод | URL |
|------|-----|
| GET | `/api/tags/` |
| POST | `/api/tags/` |
| PUT / PATCH | `/api/tags/{id}/` |
| DELETE | `/api/tags/{id}/` |
 
### 🔁 Recurring

| Метод | URL |
|------|-----|
| GET | `/api/recurring/` |
| POST | `/api/recurring/` |
| PUT / PATCH | `/api/recurring/{id}/` |
| DELETE | `/api/recurring/{id}/` |

---

### 🎯 Goals

| Метод | URL |
|------|-----|
| GET | `/api/goals/` |
| POST | `/api/goals/` |
| PUT / PATCH | `/api/goals/{id}/` |
| DELETE | `/api/goals/{id}/` |

---

### 💰 Budgets

| Метод | URL |
|------|-----|
| GET | `/api/budgets/` |
| POST | `/api/budgets/` |
| PUT / PATCH | `/api/budgets/{id}/` |
| DELETE | `/api/budgets/{id}/` |

---

### 🔔 Notifications

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
### Celery задачи
- Регулярные транзакции (ежедневно)
- Проверка бюджетов
- Уведомления
---

## 📌 Коды ответов

| Код | Значение |
|-----|---------|
| 200 | OK |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 404 | Not Found |