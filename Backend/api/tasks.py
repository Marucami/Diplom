from celery import shared_task
from datetime import date, timedelta
from django.db.models import Sum

from .models import RecurringTransaction, Transaction, Notification, User, Budget


@shared_task
def process_recurring_transactions():
    today = date.today()
    count = 0

    qs = RecurringTransaction.objects.filter(is_active=True, next_date__lte=today)

    for rt in qs:
        Transaction.objects.create(
            amount=rt.amount,
            date=today,
            description=f"[Авто] {rt.name}",
            type=rt.type,
            account=rt.account,
            category=rt.category,
            owner=rt.owner
        )
        
        if rt.frequency == "D":
            rt.next_date += timedelta(days=1)

        elif rt.frequency == "W":
            rt.next_date += timedelta(weeks=1)

        elif rt.frequency == "M":
            next_month = rt.next_date.replace(day=1) + timedelta(days=32)
            rt.next_date = next_month.replace(day=min(rt.next_date.day, 28))

        elif rt.frequency == "Y":
            rt.next_date = rt.next_date.replace(year=rt.next_date.year + 1)

        rt.save(update_fields=["next_date"])
        count += 1

    return f"Created: {count}"


@shared_task
def check_budgets(user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return f"No user {user_id}"

    today = date.today()
    month_start = today.replace(day=1)

    budgets = (
        Budget.objects
        .filter(owner=user, month=month_start)
        .select_related("category")
    )

    for b in budgets:
        spent = (
            Transaction.objects
            .filter(
                owner=user,
                category=b.category,
                type="EX",
                date__year=today.year,
                date__month=today.month
            )
            .aggregate(total=Sum("amount"))["total"] or 0
        )

        if spent > b.amount:
            Notification.objects.get_or_create(
                user=user,
                type="BE",
                message=f"{b.category.name}: превышение на {spent - b.amount}",
                link=f"/budgets/{b.id}"
            )

    return f"Checked budgets for {user_id}"


@shared_task
def send_notification(notification_id):
    try:
        n = Notification.objects.get(id=notification_id)
    except Notification.DoesNotExist:
        return f"Notification {notification_id} not found"

    # пока просто заглушка для уведов
    print(f"[notify] {n.message}")

    return f"Done: {notification_id}"