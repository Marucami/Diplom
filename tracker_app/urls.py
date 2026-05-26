from django.urls import path
from .views import auth_view, dashboard_view, logout_view

urlpatterns = [
    path('', dashboard_view, name='dashboard'),
    path('login/', auth_view, name='login'),
    path('logout/', logout_view, name='logout'),
    # path('accounts/', accounts_view, name='accounts'),
    # path('categories/', categories_view, name='categories'),
    # path('analytics/', analytics_view, name='analytics'),
    # path('transactions/', transactions_view, name='transactions'),
]
