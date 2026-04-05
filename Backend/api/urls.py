from django.urls import path
from api.views import (
    RegisterView, LoginView, LogoutView,
    TransactionView, CategoryView,
    AnalyticsView, ForecastView
)

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('login/', LoginView.as_view()),
    path('logout/', LogoutView.as_view()),

    path('transactions/', TransactionView.as_view()),
    path('categories/', CategoryView.as_view()),

    path('analytics/', AnalyticsView.as_view()),
    path('forecast/', ForecastView.as_view()),
]