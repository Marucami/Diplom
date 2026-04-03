from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Sum

from .models import Transaction, Notification, Goal
from .tasks import check_budgets


def update_account_balance(account):
    income = account.transactions.filter(type="IN").aggregate(total=Sum("amount"))["total"] or 0
    expense = account.transactions.filter(type="EX").aggregate(total=Sum("amount"))["total"] or 0

    account.balance = income - expense
    account.save(update_fields=["balance"])


def update_category_balance(category):
    income = category.transactions.filter(type="IN").aggregate(total=Sum("amount"))["total"] or 0
    expense = category.transactions.filter(type="EX").aggregate(total=Sum("amount"))["total"] or 0

    category.balance = income - expense
    category.save(update_fields=["balance"])


@receiver(post_save, sender=Transaction)
def on_transaction_save(sender, instance, **kwargs):
    # обновляем баланс
    update_account_balance(instance.account)

    if instance.category:
        update_category_balance(instance.category)

        # проверяем цели
        goals = Goal.objects.filter(
            category=instance.category,
            target_amount__lte=instance.category.balance
        )

        for goal in goals:
            Notification.objects.get_or_create(
                user=instance.owner,
                type="GR",
                message=f"Цель «{goal.name}» достигнута 🎉",
                link=f"/goals/{goal.id}"
            )

    # проверка бюджетов (асинхронно)
    check_budgets.delay(instance.owner.id)


@receiver(post_delete, sender=Transaction)
def on_transaction_delete(sender, instance, **kwargs):
    update_account_balance(instance.account)

    if instance.category:
        update_category_balance(instance.category)