from django.urls import path, include
from rest_framework.routers import DefaultRouter
from jwt_auth.views import JSONWebToken, RefreshJSONWebToken
from .views import (
    RegisterView, AccountViewSet, CategoryViewSet, TagViewSet,
    TransactionViewSet, RecurringTransactionViewSet, GoalViewSet,
    BudgetViewSet, NotificationViewSet, AnalyticsViewSet
)

router = DefaultRouter()
router.register(r'accounts', AccountViewSet, basename='account')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'tags', TagViewSet, basename='tag')
router.register(r'transactions', TransactionViewSet, basename='transaction')
router.register(r'recurring', RecurringTransactionViewSet, basename='recurring')
router.register(r'goals', GoalViewSet, basename='goal')
router.register(r'budgets', BudgetViewSet, basename='budget')
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'analytics', AnalyticsViewSet, basename='analytics')

urlpatterns = [
    path('', include(router.urls)),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', JSONWebToken.as_view(), name='jwt_login'),
    path('token/refresh/', RefreshJSONWebToken.as_view(), name='jwt_refresh'),
]