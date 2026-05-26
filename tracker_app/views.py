from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required

def auth_view(request):
    if request.method == 'POST':
        action_type = request.POST.get('action_type')
        
        # Обработка Входа
        if action_type == 'login':
            form = AuthenticationForm(request, data=request.POST)
            if form.is_valid():
                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password')
                user = authenticate(username=username, password=password)
                if user is not None:
                    login(request, user)
                    return redirect('dashboard')
            return render(request, 'register/login.html', {'error': 'Неверный логин или пароль'})
            
        elif action_type == 'register':
            data = request.POST
            first_name = data.get('first_name')
            email = data.get('email')
            password = data.get('password')
            password_confirm = data.get('password_confirm')

            if password != password_confirm:
                return render(request, 'register/login.html', {'error': 'Пароли не совпадают'})
            if User.objects.filter(username=email).exists():
                return render(request, 'register/login.html', {'error': 'Эта почта уже используется'})

            user = User.objects.create_user(username=email, email=email, password=password, first_name=first_name)
            login(request, user)
            return redirect('dashboard')

    return render(request, 'register/login.html')


@login_required(login_url='login')
def dashboard_view(request):
    # Пока передаем пустой контекст, так как база данных пустая
    context = {
        'active_tab': 'main',
    }
    return render(request, 'pages/dashboard.html', context)


def logout_view(request):
    logout(request)
    return redirect('login')
