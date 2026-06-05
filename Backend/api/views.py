from api.models import Account, Transaction, Category
from api.serializers import AccountSerializer, TransactionSerializer, CategorySerializer
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from api.services.finance_service import FinanceService
from api.services.analytics_service import AnalyticsService

# ---------------- AUTH ----------------

class RegisterView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response({"error": "Username and password required"}, status=400)

        if User.objects.filter(username=username).exists():
            return Response({"error": "User already exists"}, status=400)

        user = User.objects.create_user(username=username, password=password)
        return Response({"message": "User created"}, status=201)


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

# ---------------- TRANSACTIONS ----------------

class TransactionView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        transactions = Transaction.objects.filter(owner=request.user)
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data)

    def post(self, request):
        service = FinanceService()

        try:
            transaction = service.create_transaction(request.user, request.data)
            serializer = TransactionSerializer(transaction)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=400)


# ---------------- CATEGORIES ----------------

class CategoryView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        categories = Category.objects.filter(owner=request.user)
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CategorySerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response(serializer.data, status=201)

        return Response(serializer.errors, status=400)


# ---------------- ANALYTICS ----------------

class AnalyticsView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        service = FinanceService()
        stats = service.get_statistics(request.user)
        return Response(stats)


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
            "username": request.user.username
        })