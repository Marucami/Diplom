from django.urls import path

from .views import (
    dashboard_view,
    login_view,
    logout_view,
    transactions_view,
    categories_view,
    accounts_view,
    analytics_view,
)

urlpatterns = [
    path('', dashboard_view, name='dashboard'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('transactions/', transactions_view,name='transactions' ),
    path('categories/',categories_view,name='categories'),
    path('accounts/',accounts_view, name='accounts'),
    path('analytics/',analytics_view,name='analytics'),
]