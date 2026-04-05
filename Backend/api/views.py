from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

from api.models import Transaction, Category
from api.serializers import TransactionSerializer, CategorySerializer
from api.services.finance_service import FinanceService
from api.services.analytics_service import AnalyticsService


# ---------------- AUTH ----------------

class RegisterView(APIView):
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
    def post(self, request):
        user = authenticate(
            username=request.data.get("username"),
            password=request.data.get("password")
        )

        if user:
            login(request, user)
            return Response({"message": "Logged in"})
        return Response({"error": "Invalid credentials"}, status=401)


class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response({"message": "Logged out"})


# ---------------- TRANSACTIONS ----------------

class TransactionView(APIView):
    def get(self, request):
        transactions = Transaction.objects.filter(user=request.user)
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
    def get(self, request):
        categories = Category.objects.filter(user=request.user)
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CategorySerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=201)

        return Response(serializer.errors, status=400)


# ---------------- ANALYTICS ----------------

class AnalyticsView(APIView):
    def get(self, request):
        service = FinanceService()
        stats = service.get_statistics(request.user)
        return Response(stats)


# ---------------- FORECAST ----------------

class ForecastView(APIView):
    def get(self, request):
        try:
            goal = float(request.query_params.get("goal", 0))
        except ValueError:
            return Response({"error": "Invalid goal value"}, status=400)

        service = AnalyticsService()
        result = service.forecast_goal(request.user, goal)

        return Response(result)