from decimal import Decimal

from django.db.models import Sum

from api.models import Transaction, Account, Category


class FinanceService:

    def create_transaction(self, user, data):

        required_fields = [
            "amount",
            "category_id",
            "type",
            "date",
            "account_id"
        ]

        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing field: {field}")

        transaction = Transaction.objects.create(
            owner=user,
            amount=Decimal(data["amount"]),
            category_id=data["category_id"],
            account_id=data["account_id"],
            type=data["type"],
            date=data["date"],
            description=data.get("description", "")
        )

        self.apply_transaction(transaction)

        return transaction

    def update_transaction(self, transaction, data):

        self.rollback_transaction(transaction)

        transaction.amount = Decimal(data.get("amount", transaction.amount))

        transaction.type = data.get("type",transaction.type)

        transaction.description = data.get("description",transaction.description)

        transaction.date = data.get("date", transaction.date)

        if "category_id" in data:
            transaction.category_id = data["category_id"]

        if "account_id" in data:
            transaction.account_id = data["account_id"]

        transaction.save()

        self.apply_transaction(transaction)

        return transaction

    def delete_transaction(self, transaction):

        self.rollback_transaction(transaction)

        transaction.delete()

    def apply_transaction(self, transaction):

        amount = transaction.amount

        account = transaction.account
        category = transaction.category

        if transaction.type == Transaction.Type.INCOME:

            account.balance += amount

            if category:
                category.balance += amount

        elif transaction.type == Transaction.Type.EXPENSE:

            account.balance -= amount

            if category:
                category.balance -= amount

        account.save()

        if category:
            category.save()

    def rollback_transaction(self, transaction):

        amount = transaction.amount

        account = transaction.account
        category = transaction.category

        if transaction.type == Transaction.Type.INCOME:

            account.balance -= amount

            if category:
                category.balance -= amount

        elif transaction.type == Transaction.Type.EXPENSE:

            account.balance += amount

            if category:
                category.balance += amount

        account.save()

        if category:
            category.save()

    def get_statistics(self, user):

        income_sum = (
            Transaction.objects.filter(
                owner=user,
                type=Transaction.Type.INCOME
            ).aggregate(
                total=Sum("amount")
            )["total"] or Decimal("0")
        )

        expense_sum = (
            Transaction.objects.filter(
                owner=user,
                type=Transaction.Type.EXPENSE
            ).aggregate(
                total=Sum("amount")
            )["total"] or Decimal("0")
        )

        return {
            "income": income_sum,
            "expense": expense_sum,
            "balance": income_sum - expense_sum
        }