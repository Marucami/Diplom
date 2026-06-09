from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from decimal import Decimal
from api.models import Account, Transaction, Goal
from api.services.finance_service import FinanceService


# ==========================================
# 1. КОНТРОЛЛЕР СТРАНИЦЫ ВХОДА (LOGIN)
# ==========================================
def login_view(request):
    # Если пользователь уже залогинен, сразу отправляем его на главную
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            # Получаем объект проверенного пользователя и авторизуем сессию
            user = form.get_user()
            login(request, user)
            return redirect("dashboard")
    else:
        form = AuthenticationForm()

    # Обратите внимание на путь к шаблону: регистр папок должен точно совпадать с вашей файловой системой
    return render(request, "register/login.html", {"form": form})


# ==========================================
# 2. КОНТРОЛЛЕР СТРАНИЦЫ ВЫХОДА (LOGOUT)
# ==========================================
def logout_view(request):
    logout(request)
    return redirect("login")


# ==========================================
# 3. КОНТРОЛЛЕР ГЛАВНОЙ СТРАНИЦЫ (DASHBOARD)
# ==========================================
@login_required
def dashboard_view(request):
    user = request.user

    # ЦЕЛИ
    goals = Goal.objects.filter(owner=user)
    goals = sorted(goals, key=lambda g: g.progress_percent, reverse=True)[:3]

    # Счета пользователя
    accounts = Account.objects.filter(owner=user).order_by("-created_at")[:3]
    total_balance = Account.objects.filter(owner=user).aggregate(Sum("balance"))[
        "balance__sum"
    ] or Decimal("0")

    # ТРАНЗАКЦИИ
    last_transactions = (
        Transaction.objects.filter(owner=user)
        .select_related("account", "category")
        .order_by("-date", "-id")[:2]
    )

    # Расходы по категориям для Chart.js
    categories = [
        "Продукты",
        "Транспорт",
        "Развлечения",
        "Жильё",
        "Рестораны",
        "Другое",
    ]

    chart_data = []

    for cat in categories:
        amount = Transaction.objects.filter(
            owner=user, type=Transaction.Type.EXPENSE, category__name=cat
        ).aggregate(Sum("amount"))["amount__sum"] or Decimal("0")

        chart_data.append(float(amount))

    # План расходов на месяц
    monthly_plan = Transaction.objects.filter(
        owner=user, type=Transaction.Type.EXPENSE
    ).aggregate(total=Sum("amount"))["total"] or Decimal("0")

    service = FinanceService()
    stats = service.get_statistics(user)

    expense = stats["expense"] or Decimal("0")

    if monthly_plan > Decimal("0"):
        monthly_progress = min(round(expense / monthly_plan * Decimal("100")), 100)
    else:
        monthly_progress = 0

    context = {
        "accounts": accounts,
        "total_balance": total_balance,
        "chart_data": chart_data,
        "income": stats["income"],
        "expense": stats["expense"],
        "goals": goals,
        "monthly_plan": monthly_plan,
        "last_transactions": last_transactions,
        "monthly_progress": monthly_progress,
    }

    return render(request, "pages/dashboard.html", context)


# Тимоша добавил
@login_required
def transactions_view(request):
    return render(request, "pages/transactions.html")


@login_required
def categories_view(request):
    return render(request, "pages/categories.html")


@login_required
def accounts_view(request):
    return render(request, "pages/bank_accounts.html")


@login_required
def analytics_view(request):
    return render(request, "pages/analytics.html")
