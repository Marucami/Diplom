from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
import os
from decimal import Decimal


class Account(models.Model):
    name = models.CharField(max_length=100)
    bank = models.ForeignKey(
        "AvailableBank", on_delete=models.SET_NULL, null=True, blank=True
    )
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default="RUB")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="accounts")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.owner})"


class Category(models.Model):
    class Type(models.TextChoices):
        INCOME = "IN", "Доход"
        EXPENSE = "EX", "Расход"
        BOTH = "BO", "Оба"
        GOAL = "GL", "Бессрочная цель"

    class Status(models.TextChoices):
        ACTIVE = "AC", "Активная"
        FROZEN = "FR", "Заморожена"
        POTENTIAL = "PO", "Потенциальная"

    name = models.CharField(max_length=100)
    type = models.CharField(max_length=2, choices=Type.choices, default=Type.BOTH)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    target_amount = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True, default=0
    )

    status = models.CharField(
        max_length=2, choices=Status.choices, default=Status.ACTIVE
    )
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="categories")
    created_at = models.DateTimeField(auto_now_add=True)
    deadline = models.DateField(null=True, blank=True)

    template = models.ForeignKey(
        "AvailableCategoryTemplate",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="categories",
    )

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=7, default="#808080")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tags")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("name", "owner")

    def __str__(self):
        return self.name


class Transaction(models.Model):
    class Type(models.TextChoices):
        INCOME = "IN", "Доход"
        EXPENSE = "EX", "Расход"

    amount = models.DecimalField(
        max_digits=12, decimal_places=2, validators=[MinValueValidator(0.01)]
    )
    date = models.DateField()
    description = models.CharField(max_length=255, blank=True)
    type = models.CharField(max_length=2, choices=Type.choices)

    account = models.ForeignKey(
        Account, on_delete=models.CASCADE, related_name="transactions"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transactions",
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name="transactions")

    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="transactions"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_type_display()} {self.amount} ({self.date})"


class RecurringTransaction(models.Model):
    class Frequency(models.TextChoices):
        DAILY = "D", "Каждый день"
        WEEKLY = "W", "Раз в неделю"
        MONTHLY = "M", "Раз в месяц"
        YEARLY = "Y", "Раз в год"

    name = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    type = models.CharField(max_length=2, choices=Transaction.Type.choices)

    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True
    )

    frequency = models.CharField(max_length=1, choices=Frequency.choices)
    next_date = models.DateField()
    is_active = models.BooleanField(default=True)

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="recurring")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.get_frequency_display()})"


class Goal(models.Model):
    name = models.CharField(max_length=100)
    target_amount = models.DecimalField(max_digits=12, decimal_places=2)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="goals"
    )

    deadline = models.DateField(null=True, blank=True)

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="goals")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @property
    def current_amount(self):
        if not self.category or self.category.balance is None:
            return Decimal("0")

        return max(Decimal("0"), self.category.balance)

    def progress_percent(self):
        if not self.target_amount or self.target_amount <= Decimal("0"):
            return 0

        current = self.current_amount or Decimal("0")

        progress = (current / self.target_amount) * Decimal("100")

        return max(0, min(100, int(progress)))


class Budget(models.Model):
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="budgets"
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    month = models.DateField()

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="budgets")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("category", "month", "owner")

    def __str__(self):
        return f"{self.category} — {self.month}"


class Notification(models.Model):
    class Type(models.TextChoices):
        BUDGET_EXCEEDED = "BE", "Бюджет превышен"
        GOAL_REACHED = "GR", "Цель достигнута"
        DEADLINE = "GD", "Скоро дедлайн"
        RECURRING = "RC", "Регулярный платёж"
        OTHER = "OT", "Другое"

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notifications"
    )
    type = models.CharField(max_length=2, choices=Type.choices, default=Type.OTHER)
    title = models.CharField(max_length=200, blank=True, null=True)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    link = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_type_display()} ({self.user})"


# ЗАПОЛНЯТЬ ЧЕРЕЗ АДМИНКУ :(
class AvailableBank(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название банка")
    color_hex = models.CharField(
        max_length=7, default="#ffffff", verbose_name="Цвет (HEX)"
    )

    class Meta:
        verbose_name = "Доступный банк"
        verbose_name_plural = "Доступные банки"

    def __str__(self):
        return self.name


def category_icon_upload_path(instance, filename):
    ext = filename.split(".")[-1]
    # Используем имя категории для сохранения, очистив от лишних пробелов
    safe_name = "".join(
        [c for c in instance.name if c.isalpha() or c.isdigit()]
    ).rstrip()
    return os.path.join("category_icons", f"{safe_name}.{ext}")


class AvailableCategoryTemplate(models.Model):
    name = models.CharField(
        max_length=100, unique=True, verbose_name="Название шаблона"
    )

    TYPE_CHOICES = [
        ("EX", "Ежемесячные траты / Накопления"),
        ("GL", "Бессрочная цель"),
        ("IN", "Доход"),
    ]
    type = models.CharField(
        max_length=2,
        choices=TYPE_CHOICES,
        default="EX",
        verbose_name="Тип по умолчанию",
    )

    # Поле цвета (HEX) — совпадает с тем, что ожидает фронтенд (t.color_hex)
    color_hex = models.CharField(
        max_length=7, default="#2c8a93", verbose_name="Цвет темы (HEX)"
    )

    # Оставляем строку, но в админке сделаем выпадающий список
    icon_name = models.CharField(
        max_length=100, default="wallet1.png", verbose_name="Имя файла иконки"
    )

    class Meta:
        verbose_name = "Шаблон категории"
        verbose_name_plural = "Шаблоны категорий"

    def __str__(self):
        return self.name
