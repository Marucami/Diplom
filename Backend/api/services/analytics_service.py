from django.db.models import Sum
from django.utils.timezone import now
from datetime import timedelta
from api.models import Transaction


class AnalyticsService:

    def forecast_goal(self, user, goal_amount):
        transactions = Transaction.objects.filter(user=user)

        if not transactions.exists():
            return {"error": "Not enough data"}

        last_month = now() - timedelta(days=30)

        monthly_income = transactions.filter(
            type="income",
            date__gte=last_month
        ).aggregate(Sum("amount"))["amount__sum"] or 0

        monthly_expense = transactions.filter(
            type="expense",
            date__gte=last_month
        ).aggregate(Sum("amount"))["amount__sum"] or 0

        net = monthly_income - monthly_expense

        if net <= 0:
            return {"error": "Goal unreachable"}

        months = goal_amount / net

        return {
            "monthly_income": round(monthly_income, 2),
            "monthly_expense": round(monthly_expense, 2),
            "net_income": round(net, 2),
            "months_to_reach": round(months, 2)
        }