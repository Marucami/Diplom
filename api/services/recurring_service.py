from datetime import timedelta

from dateutil.relativedelta import relativedelta
from django.utils import timezone

from api.models import RecurringTransaction
from api.services.finance_service import FinanceService


class RecurringTransactionService:

    @staticmethod
    def process_due_transactions():

        today = timezone.now().date()

        recurring_transactions = RecurringTransaction.objects.filter(
            is_active=True, next_date__lte=today
        )

        finance_service = FinanceService()

        for recurring in recurring_transactions:

            finance_service.create_transaction(
                recurring.owner,
                {
                    "account": recurring.account.id,
                    "category": (recurring.category.id if recurring.category else None),
                    "amount": recurring.amount,
                    "type": recurring.type,
                    "description": (f"Автоплатёж: {recurring.name}"),
                    "date": today,
                },
            )

            if recurring.frequency == RecurringTransaction.Frequency.DAILY:
                recurring.next_date += timedelta(days=1)

            elif recurring.frequency == RecurringTransaction.Frequency.WEEKLY:
                recurring.next_date += timedelta(days=7)

            elif recurring.frequency == RecurringTransaction.Frequency.MONTHLY:
                recurring.next_date += relativedelta(months=1)

            elif recurring.frequency == RecurringTransaction.Frequency.YEARLY:
                recurring.next_date += relativedelta(years=1)

            recurring.save()
