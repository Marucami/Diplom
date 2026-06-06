from django.urls import path
from api.views import (
    RegisterView, LoginView, LogoutView, AccountView, 
    TransactionView, CategoryView,
    AnalyticsView, ForecastView, MeView
)

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('login/', LoginView.as_view()),
    path('logout/', LogoutView.as_view()),
    path('accounts/', AccountView.as_view()),
    path('accounts/<int:pk>/', AccountView.as_view()),
    
    path('transactions/', TransactionView.as_view()),
    path('transactions/<int:pk>/', TransactionView.as_view()),
    
    path('categories/', CategoryView.as_view()),
    path('categories/<int:pk>/', CategoryView.as_view()),

    path('analytics/', AnalyticsView.as_view()),
    path('forecast/', ForecastView.as_view()),
    path('me/', MeView.as_view()),
]