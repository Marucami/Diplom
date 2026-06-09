from django.db.models.functions import TruncMonth
from api.models import Account, Transaction, Category
from api.serializers import AccountSerializer, TransactionSerializer, CategorySerializer, RegisterSerializer
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, login, logout
from api.services.finance_service import FinanceService
from api.services.analytics_service import AnalyticsService
from django.shortcuts import get_object_or_404
from .models import AvailableBank, AvailableCategoryTemplate
from django.db.models import Sum, Value, DecimalField
from django.db.models.functions import Coalesce
from rest_framework.pagination import PageNumberPagination
from rest_framework.authentication import SessionAuthentication
from dateutil.relativedelta import relativedelta 
from django.utils import timezone
from datetime import timedelta

# ---------------- AUTH ----------------

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):

        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():

            user = serializer.save()

            login(request, user)

            return Response(
                {
                    "message": "User created successfully",
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "authenticated": True
                },
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        user = authenticate(
            username=request.data.get("username"),
            password=request.data.get("password")
        )

        if user:
            login(request, user)
            return Response({
            "id": user.id,
            "username": user.username,
            "authenticated": True
            })
            
        return Response({"error": "Invalid credentials"}, status=401)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        logout(request)
        return Response({"message": "Logged out"})


# ---------------- Account ----------------

class AccountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        accounts = Account.objects.filter(owner=request.user)
        serializer = AccountSerializer(accounts, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = AccountSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response(serializer.data, status=201)

        return Response(serializer.errors, status=400)

    def put(self, request, pk):
        account = get_object_or_404(Account,pk=pk,owner=request.user)

        serializer = AccountSerializer(account,data=request.data,partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        account = get_object_or_404(Account,pk=pk,owner=request.user)

        account.delete()

        return Response({"message": "Account deleted"},status=204)

# ---------------- TRANSACTIONS ----------------
class TransactionPagination(PageNumberPagination):
    page_size = 10

class TransactionView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication] 

    def get(self, request):
        queryset = Transaction.objects.filter(owner=request.user).order_by('-date', '-id')

        # === БЛОК ФИЛЬТРАЦИИ ===
        month_param = request.query_params.get('month')
        if month_param and '-' in month_param:
            try:
                year, month = month_param.split('-')
                queryset = queryset.filter(date__year=year, date__month=month)
            except (ValueError, TypeError):
                pass 

        category_param = request.query_params.get('category')
        if category_param:
            queryset = queryset.filter(category_id=category_param)

        account_param = request.query_params.get('account')
        if account_param:
            queryset = queryset.filter(account_id=account_param)

        search_param = request.query_params.get('search')
        if search_param:
            queryset = queryset.filter(description__icontains=search_param)

        # === БЛОК ПАГИНАЦИИ ===
        paginator = TransactionPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)
        
        if page is not None:
            serializer = TransactionSerializer(page, many=True, context={"request": request})
            return paginator.get_paginated_response(serializer.data)

        serializer = TransactionSerializer(queryset, many=True, context={"request": request})
        return Response(serializer.data)

    def post(self, request):
        service = FinanceService()
        try:
            transaction = service.create_transaction(request.user, request.data)
            serializer = TransactionSerializer(transaction, context={"request": request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=400)

    def put(self, request, pk):
        transaction = get_object_or_404(Transaction, pk=pk, owner=request.user)
        service = FinanceService()
        try:
            transaction = service.update_transaction(transaction, request.data)
            serializer = TransactionSerializer(transaction, context={"request": request})
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=400)

    def delete(self, request, pk):
        transaction = get_object_or_404(Transaction, pk=pk, owner=request.user)
        service = FinanceService()
        service.delete_transaction(transaction)
        return Response({"message": "Transaction deleted"}, status=204)

# ---------------- CATEGORIES ----------------

class CategoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        categories = Category.objects.filter(owner=request.user).annotate(
            total_balance=Coalesce(
                Sum('transactions__amount'), 
                Value(0.0), 
                output_field=DecimalField()
            )
        )
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CategorySerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response(serializer.data, status=201)

        return Response(serializer.errors, status=400)

    def put(self, request, pk):
        category = get_object_or_404(Category,pk=pk,owner=request.user)

        serializer = CategorySerializer(category,data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        category = get_object_or_404(Category,pk=pk,owner=request.user)

        category.delete()

        return Response({"message": "Category deleted"},status=204)


# ---------------- ANALYTICS ----------------

class AnalyticsView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication]

    def get(self, request):
        user = request.user
        now = timezone.now().date()
        
        # Генерируем список последних 6 месяцев (от -5 до текущего)
        months_list = [now - relativedelta(months=i) for i in range(5, -1, -1)]

        # Словари для локализации
        months_ru = {
            1: 'Янв', 2: 'Фев', 3: 'Март', 4: 'Апр', 5: 'Май', 6: 'Июнь',
            7: 'Июль', 8: 'Авг', 9: 'Сент', 10: 'Окт', 11: 'Ноя', 12: 'Дек'
        }
        months_ru_full = {
            1: 'Январь', 2: 'Февраль', 3: 'Март', 4: 'Апрель', 5: 'Май', 6: 'Июнь',
            7: 'Июль', 8: 'Август', 9: 'Сентябрь', 10: 'Октябрь', 11: 'Ноябрь', 12: 'Декабрь'
        }

        # Инициализируем чистую структуру (по дефолту везде нули)
        raw_data = {
            'EX': {m.strftime('%Y-%m'): 0.0 for m in months_list}, # Расходы
            'IN': {m.strftime('%Y-%m'): 0.0 for m in months_list}  # Доходы
        }

        # Точка старта фильтрации базы данных (первый день самого старого месяца из 6)
        start_date = months_list[0].replace(day=1)

        # 1. Запрос агрегированных данных ИМЕННО с фильтрацией по владельцу и датам
        monthly_stats = (
            Transaction.objects.filter(owner=user, date__gte=start_date, date__lte=now)
            .annotate(month=TruncMonth('date'))  # <-- ИСПРАВЛЕНО ЗДЕСЬ (просто TruncMonth)
            .values('month', 'type')
            .annotate(total_amount=Sum('amount'))
            .order_by('month')
        )

        # Раскладываем агрегированные суммы по полочкам (EX к EX, IN к IN)
        for entry in monthly_stats:
            if not entry['month']:
                continue
            m_key = entry['month'].strftime('%Y-%m')
            t_type = entry['type']  # 'EX' или 'IN'
            if t_type in raw_data and m_key in raw_data[t_type]:
                # Сохраняем абсолютное значение (без минусов для расходов)
                raw_data[t_type][m_key] = float(abs(entry['total_amount'] or 0))

        # 2. Запрос атомарных транзакций текущего месяца (для точных min / max)
        current_month_start = now.replace(day=1)
        current_month_txs = Transaction.objects.filter(
            owner=user, 
            date__gte=current_month_start, 
            date__lte=now
        ).values('type', 'amount')

        # Распределяем отдельные операции текущего месяца по спискам
        current_ops = {'EX': [], 'IN': []}
        for tx in current_month_txs:
            t_type = tx['type']
            if t_type in current_ops:
                current_ops[t_type].append(float(abs(tx['amount'] or 0)))

        # Функция-сборщик датасета для конкретного типа ('EX' или 'IN')
        def build_dataset_for_type(t_type):
            chart_labels = []
            chart_values = []
            table_rows = []
            prev_amount = None

            for m in months_list:
                m_key = m.strftime('%Y-%m')
                amount = raw_data[t_type][m_key]

                # Данные графиков
                chart_labels.append(months_ru[m.month])
                chart_values.append(amount)

                # Расчет процентов разницы с прошлым месяцем
                diff_pct = None
                if prev_amount is not None:
                    if prev_amount > 0:
                        diff_val = amount - prev_amount
                        diff_pct = round((diff_val / prev_amount) * 100)
                    elif prev_amount == 0 and amount > 0:
                        diff_pct = 100  # С нуля выросли на 100%

                table_rows.append({
                    'name': months_ru_full[m.month],
                    'value': amount,
                    'percentage': diff_pct
                })
                prev_amount = amount

            # Возвращаем структуру, готовую к употреблению фронтендом
            return {
                'labels': chart_labels,
                'values': chart_values,
                'months': table_rows,
                # Если транзакций нет, вернется пустой список [], и фронтенд запишет 0 по дефолту
                'current_month_operations': current_ops[t_type] 
            }

        # Формируем итоговый ответ с разделением, которое ждет фронтенд
        response_data = {
            'expenses': build_dataset_for_type('EX'),
            'incomes': build_dataset_for_type('IN')
        }

        return Response(response_data)


# ---------------- FORECAST ----------------

class ForecastView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            goal = float(request.query_params.get("goal", 0))
        except ValueError:
            return Response({"error": "Invalid goal value"}, status=400)

        service = AnalyticsService()
        result = service.forecast_goal(request.user, goal)

        return Response(result)


#-------------------Endpoint для текущего пользователя--------------------
class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "id": request.user.id,
            "username": request.user.username,
            "first_name": request.user.first_name
        })
        
# Эндпоинт для выпадающего списка банков
class AvailableBanksListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        data = AvailableBank.objects.all().values('id', 'name', 'color_hex')
        return Response(list(data))

# Эндпоинт для выпадающего списка категорий
class AvailableCategoriesListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        templates = AvailableCategoryTemplate.objects.all()
        
        serialized_data = []
        for t in templates:
            serialized_data.append({
                "id": t.id,
                "name": t.name,
                "type": t.type,
                "color_hex": t.color_hex,
                "icon": f"/static/icons/{t.icon_name}"  
            })
            
        return Response(serialized_data)