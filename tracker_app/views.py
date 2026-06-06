from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from api.models import Account, Transaction 
from api.services.finance_service import FinanceService

# ==========================================
# 1. КОНТРОЛЛЕР СТРАНИЦЫ ВХОДА (LOGIN)
# ==========================================
def login_view(request):
    # Если пользователь уже залогинен, сразу отправляем его на главную
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            # Получаем объект проверенного пользователя и авторизуем сессию
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
        
    # Обратите внимание на путь к шаблону: регистр папок должен точно совпадать с вашей файловой системой
    return render(request, 'register/login.html', {'form': form})

# ==========================================
# 2. КОНТРОЛЛЕР СТРАНИЦЫ ВЫХОДА (LOGOUT)
# ==========================================
def logout_view(request):
    logout(request)
    return redirect('login')

# ==========================================
# 3. КОНТРОЛЛЕР ГЛАВНОЙ СТРАНИЦЫ (DASHBOARD)
# ==========================================
@login_required
def dashboard_view(request):
    user = request.user
    
    # Счета пользователя
    accounts = Account.objects.filter(owner=user)
    total_balance = accounts.aggregate(Sum('balance'))['balance__sum'] or 0
    
    # Расходы по категориям для Chart.js
    categories = ['Продукты', 'Транспорт', 'Развлечения', 'Жильё', 'Рестораны', 'Другое']
    chart_data = []
    
    for cat in categories:
        amount = Transaction.objects.filter(
            owner=user, 
            type=Transaction.Type.EXPENSE, 
            category__name=cat
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        chart_data.append(float(amount))
        # Я добавил тут 
    service = FinanceService()
    stats = service.get_statistics(user)
    context = {
        'accounts': accounts,
        'total_balance': total_balance,
        'chart_data': chart_data,
        'income': stats['income'],
        'expense': stats['expense'],
    }
    return render(request, 'pages/dashboard.html', context)

# Тимоша добавил
@login_required
def transactions_view(request):
    return render(
        request,
        'pages/transactions.html'
    )

@login_required
def categories_view(request):
    return render(
        request,
        'pages/categories.html'
    )

@login_required
def accounts_view(request):
    return render(
        request,
        'pages/bank_accounts.html'
    )

@login_required
def analytics_view(request):
    return render(
        request,
        'pages/analytics.html'
    )