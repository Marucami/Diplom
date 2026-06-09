from datetime import timedelta

from django.db.models import Sum
from django.utils.timezone import now

from api.models import Transaction


class AnalyticsService:

    def forecast_goal(self, user, goal_amount):

        transactions = Transaction.objects.filter(owner=user)

        if not transactions.exists():
            return {"error": "Not enough data"}

        last_month = now().date() - timedelta(days=30)
        monthly_income = (
            transactions.filter(
                type=Transaction.Type.INCOME, date__gte=last_month
            ).aggregate(total=Sum("amount"))["total"]
            or 0
        )
        monthly_expense = (
            transactions.filter(
                type=Transaction.Type.EXPENSE, date__gte=last_month
            ).aggregate(total=Sum("amount"))["total"]
            or 0
        )
        net = monthly_income - monthly_expense

        if net <= 0:
            return {"error": "Goal unreachable"}
        months = goal_amount / net
        return {
            "monthly_income": round(float(monthly_income), 2),
            "monthly_expense": round(float(monthly_expense), 2),
            "net_income": round(float(net), 2),
            "months_to_reach": round(float(months), 2),
        }
