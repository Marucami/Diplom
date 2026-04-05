from django.db.models import Sum
from api.models import Transaction


class AnalyticsService:

    def forecast_goal(self, user, goal_amount):
        transactions = Transaction.objects.filter(user=user)

        if not transactions.exists():
            return {"error": "Not enough data"}

        income = transactions.filter(type="income").aggregate(Sum("amount"))["amount__sum"] or 0
        expense = transactions.filter(type="expense").aggregate(Sum("amount"))["amount__sum"] or 0

        total_transactions = transactions.count()

        avg_income = income / total_transactions
        avg_expense = expense / total_transactions

        net_income = avg_income - avg_expense

        if net_income <= 0:
            return {"error": "Goal is not reachable with current spending"}

        months = goal_amount / net_income

        return {
            "goal": goal_amount,
            "avg_income": round(avg_income, 2),
            "avg_expense": round(avg_expense, 2),
            "net_income": round(net_income, 2),
            "months_to_reach": round(months, 2)
        }