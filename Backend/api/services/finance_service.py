from django.db.models import Sum
from api.models import Transaction, Category


class FinanceService:

    def create_transaction(self, user, data):
        if not all(k in data for k in ("amount", "category_id", "type")):
            raise ValueError("Missing required fields")

        transaction = Transaction.objects.create(
            user=user,
            amount=float(data["amount"]),
            category_id=data["category_id"],
            type=data["type"]
        )

        self.update_category_balance(transaction)

        return transaction

    def update_category_balance(self, transaction):
        category = transaction.category

        if transaction.type == "income":
            category.balance += transaction.amount
        elif transaction.type == "expense":
            category.balance -= transaction.amount

        category.save()

    def get_statistics(self, user):
        income = Transaction.objects.filter(user=user, type="income").aggregate(Sum("amount"))["amount__sum"] or 0
        expense = Transaction.objects.filter(user=user, type="expense").aggregate(Sum("amount"))["amount__sum"] or 0

        return {
            "income": income,
            "expense": expense,
            "balance": income - expense
        }

    def check_budgets(self):
        categories = Category.objects.all()

        for category in categories:
            if category.balance < 0:
                print(f"⚠️ Budget exceeded: {category.name}")