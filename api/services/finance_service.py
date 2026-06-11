from decimal import Decimal
from django.db.models import Sum
from datetime import date, timedelta
from api.models import Transaction, Account, Category, RecurringTransaction


class FinanceService:

    def create_transaction(self, user, data):

        required_fields = ["amount", "category_id", "type", "date", "account_id"]

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
            description=data.get("description", ""),
        )

        self.apply_transaction(transaction)

        return transaction

    def update_transaction(self, transaction, data):

        self.rollback_transaction(transaction)

        transaction.amount = Decimal(data.get("amount", transaction.amount))

        transaction.type = data.get("type", transaction.type)

        transaction.description = data.get("description", transaction.description)

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

        income_sum = Transaction.objects.filter(
            owner=user, type=Transaction.Type.INCOME
        ).aggregate(total=Sum("amount"))["total"] or Decimal("0")

        expense_sum = Transaction.objects.filter(
            owner=user, type=Transaction.Type.EXPENSE
        ).aggregate(total=Sum("amount"))["total"] or Decimal("0")

        return {
            "income": income_sum,
            "expense": expense_sum,
            "balance": income_sum - expense_sum,
        }

    def process_recurring_transactions(self):

        today = date.today()

        recurring_list = RecurringTransaction.objects.filter(
            is_active=True, next_date__lte=today
        )

        for recurring in recurring_list:

            self.create_transaction(
                recurring.owner,
                {
                    "amount": recurring.amount,
                    "category_id": (
                        recurring.category.id if recurring.category else None
                    ),
                    "account_id": recurring.account.id,
                    "type": recurring.type,
                    "date": today,
                    "description": f"Автоплатёж: {recurring.name}",
                },
            )

            if recurring.frequency == RecurringTransaction.Frequency.DAILY:
                recurring.next_date += timedelta(days=1)

            elif recurring.frequency == RecurringTransaction.Frequency.WEEKLY:
                recurring.next_date += timedelta(days=7)

            elif recurring.frequency == RecurringTransaction.Frequency.MONTHLY:
                recurring.next_date += timedelta(days=30)

            elif recurring.frequency == RecurringTransaction.Frequency.YEARLY:
                recurring.next_date += timedelta(days=365)

            recurring.save()
