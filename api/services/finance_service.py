from django.db.models import Sum
from api.models import Transaction, Category

class FinanceService:

    def create_transaction(self, user, data):
        required_fields = ["amount", "category_id", "type", "date", "account_id"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing field: {field}")

        transaction = Transaction.objects.create(
            owner=user,  # вместо user=user
            amount=float(data["amount"]),
            category_id=data["category_id"],
            type=data["type"],
            date=data["date"],
            account_id=data["account_id"],
            description=data.get("description", "")
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
        income = Transaction.objects.filter(owner=user, type="income").aggregate(Sum("amount"))["amount__sum"] or 0
        expense = Transaction.objects.filter(owner=user, type="expense").aggregate(Sum("amount"))["amount__sum"] or 0
        return {
            "income": income,
            "expense": expense,
            "balance": income - expense
        }