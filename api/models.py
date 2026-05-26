from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator


class Account(models.Model):
    name = models.CharField(max_length=100)
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

    class Status(models.TextChoices):
        ACTIVE = "AC", "Активная"
        FROZEN = "FR", "Заморожена"
        POTENTIAL = "PO", "Потенциальная"

    name = models.CharField(max_length=100)
    type = models.CharField(max_length=2, choices=Type.choices, default=Type.BOTH)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=2, choices=Status.choices, default=Status.ACTIVE)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="categories")
    created_at = models.DateTimeField(auto_now_add=True)

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
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    date = models.DateField()
    description = models.CharField(max_length=255, blank=True)
    type = models.CharField(max_length=2, choices=Type.choices)

    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="transactions")
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transactions"
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name="transactions")

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="transactions")
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
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)

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
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="goals")

    deadline = models.DateField(null=True, blank=True)

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="goals")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @property
    def current_amount(self):
        return self.category.balance if self.category else 0

    @property
    def progress_percent(self):
        if not self.target_amount:
            return 0

        progress = (self.current_amount / self.target_amount) * 100
        return min(100, int(progress))


class Budget(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="budgets")
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

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    type = models.CharField(max_length=2, choices=Type.choices)

    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    link = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_type_display()} ({self.user})"