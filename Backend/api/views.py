from django.shortcuts import render

# Create your views here.
from django.shortcuts import get_object_or_404
from django.db.models import Sum, Q
from django.utils import timezone
from datetime import datetime, timedelta, date
from rest_framework import viewsets, permissions, generics, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from jwt_auth import views as jwt_auth_views
from django.contrib.auth.models import User
from .models import (
    Account, Category, Tag, Transaction, RecurringTransaction,
    Goal, Budget, Notification
)
from .serializers import (
    UserSerializer, RegisterSerializer, AccountSerializer, CategorySerializer,
    TagSerializer, TransactionSerializer, RecurringTransactionSerializer,
    GoalSerializer, BudgetSerializer, NotificationSerializer
)
from .tasks import check_budgets

# ---------- Регистрация ----------
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer

# ---------- Счета ----------
class AccountViewSet(viewsets.ModelViewSet):
    serializer_class = AccountSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Account.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

# ---------- Категории ----------
class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['status', 'type']

    def get_queryset(self):
        return Category.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

# ---------- Теги ----------
class TagViewSet(viewsets.ModelViewSet):
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Tag.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

# ---------- Транзакции ----------
class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['account', 'category', 'type', 'date']
    search_fields = ['description']
    ordering_fields = ['date', 'amount', 'created_at']

    def get_queryset(self):
        return Transaction.objects.filter(owner=self.request.user).select_related('account', 'category').prefetch_related('tags')

    def perform_create(self, serializer):
        transaction = serializer.save(owner=self.request.user)
        check_budgets.delay(self.request.user.id)

    @action(detail=False, methods=['get'], url_path='export')
    def export(self, request):
        import csv
        from django.http import StreamingHttpResponse

        user = request.user
        queryset = self.filter_queryset(self.get_queryset())

        class Echo:
            def write(self, value):
                return value

        def generate_rows():
            yield ['Date', 'Type', 'Amount', 'Category', 'Account', 'Description', 'Tags']
            for t in queryset.iterator():
                tags = ', '.join([tag.name for tag in t.tags.all()])
                yield [
                    t.date.isoformat(),
                    t.get_type_display(),
                    str(t.amount),
                    t.category.name if t.category else '',
                    t.account.name,
                    t.description,
                    tags
                ]

        pseudo_buffer = Echo()
        writer = csv.writer(pseudo_buffer)
        response = StreamingHttpResponse(
            (writer.writerow(row) for row in generate_rows()),
            content_type='text/csv'
        )
        response['Content-Disposition'] = 'attachment; filename="transactions.csv"'
        return response

# ---------- Регулярные транзакции ----------
class RecurringTransactionViewSet(viewsets.ModelViewSet):
    serializer_class = RecurringTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return RecurringTransaction.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

# ---------- Цели ----------
class GoalViewSet(viewsets.ModelViewSet):
    serializer_class = GoalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Goal.objects.filter(owner=self.request.user).select_related('category')

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['get'], url_path='forecast')
    def forecast(self, request, pk=None):
        goal = self.get_object()
        user = request.user
        today = date.today()
        six_months_ago = today - timedelta(days=180)
        transactions = Transaction.objects.filter(
            owner=user,
            category=goal.category,
            date__gte=six_months_ago
        )
        total_income = transactions.filter(type='IN').aggregate(Sum('amount'))['amount__sum'] or 0
        total_expense = transactions.filter(type='EX').aggregate(Sum('amount'))['amount__sum'] or 0
        net = total_income - total_expense
        months = 6
        avg_monthly = net / months if months else 0
        remaining = goal.target_amount - goal.current_amount
        if avg_monthly > 0:
            months_to_goal = remaining / avg_monthly
        else:
            months_to_goal = None

        return Response({
            'goal_id': goal.id,
            'current_amount': goal.current_amount,
            'target_amount': goal.target_amount,
            'remaining': remaining,
            'avg_monthly_net': avg_monthly,
            'months_to_goal': months_to_goal
        })

# ---------- Бюджеты ----------
class BudgetViewSet(viewsets.ModelViewSet):
    serializer_class = BudgetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Budget.objects.filter(owner=self.request.user).select_related('category')

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

# ---------- Уведомления ----------
class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'patch', 'delete']

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')

    @action(detail=True, methods=['post'], url_path='mark-read')
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'status': 'marked as read'})

# ---------- Аналитика ----------
class AnalyticsViewSet(viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return None

    @action(detail=False, methods=['get'], url_path='summary')
    def summary(self, request):
        user = request.user
        total_income = Transaction.objects.filter(owner=user, type='IN').aggregate(Sum('amount'))['amount__sum'] or 0
        total_expense = Transaction.objects.filter(owner=user, type='EX').aggregate(Sum('amount'))['amount__sum'] or 0
        accounts_balance = Account.objects.filter(owner=user).aggregate(Sum('balance'))['balance__sum'] or 0
        top_categories = Transaction.objects.filter(owner=user, type='EX') \
            .values('category__name') \
            .annotate(total=Sum('amount')) \
            .order_by('-total')[:5]

        return Response({
            'total_income': total_income,
            'total_expense': total_expense,
            'accounts_balance': accounts_balance,
            'top_expense_categories': list(top_categories)
        })

    @action(detail=False, methods=['get'], url_path='by-period')
    def by_period(self, request):
        user = request.user
        start = request.query_params.get('start')
        end = request.query_params.get('end')
        group_by = request.query_params.get('group_by', 'month')
        if not start or not end:
            return Response({'error': 'start and end required'}, status=400)
        try:
            start_date = datetime.strptime(start, '%Y-%m-%d').date()
            end_date = datetime.strptime(end, '%Y-%m-%d').date()
        except ValueError:
            return Response({'error': 'Invalid date format, use YYYY-MM-DD'}, status=400)

        if group_by == 'day':
            trunc = models.functions.TruncDay('date')
        else:
            trunc = models.functions.TruncMonth('date')

        data = Transaction.objects.filter(
            owner=user, date__gte=start_date, date__lte=end_date
        ).annotate(period=trunc).values('period').annotate(
            income=Sum('amount', filter=Q(type='IN')),
            expense=Sum('amount', filter=Q(type='EX'))
        ).order_by('period')

        return Response(list(data))

    @action(detail=False, methods=['get'], url_path='budgets-status')
    def budgets_status(self, request):
        user = request.user
        today = date.today()
        month_start = today.replace(day=1)
        budgets = Budget.objects.filter(owner=user, month=month_start)
        data = []
        for budget in budgets:
            spent = Transaction.objects.filter(
                owner=user,
                category=budget.category,
                type='EX',
                date__year=today.year,
                date__month=today.month
            ).aggregate(total=Sum('amount'))['total'] or 0
            data.append({
                'budget_id': budget.id,
                'category_id': budget.category.id,
                'category_name': budget.category.name,
                'limit': budget.amount,
                'spent': spent,
                'remaining': budget.amount - spent,
                'percent': (spent / budget.amount * 100) if budget.amount else 0
            })
        return Response(data)

    @action(detail=False, methods=['get'], url_path='compare')
    def compare_periods(self, request):
        user = request.user
        start1 = request.query_params.get('start1')
        end1 = request.query_params.get('end1')
        start2 = request.query_params.get('start2')
        end2 = request.query_params.get('end2')
        if not all([start1, end1, start2, end2]):
            return Response({'error': 'start1, end1, start2, end2 required'}, status=400)

        def get_stats(start, end):
            return {
                'income': Transaction.objects.filter(owner=user, type='IN', date__range=[start, end]).aggregate(Sum('amount'))['amount__sum'] or 0,
                'expense': Transaction.objects.filter(owner=user, type='EX', date__range=[start, end]).aggregate(Sum('amount'))['amount__sum'] or 0,
            }
        try:
            data1 = get_stats(start1, end1)
            data2 = get_stats(start2, end2)
        except:
            return Response({'error': 'Invalid dates'}, status=400)

        return Response({
            'period1': data1,
            'period2': data2,
            'difference': {
                'income': data2['income'] - data1['income'],
                'expense': data2['expense'] - data1['expense'],
            }
        })