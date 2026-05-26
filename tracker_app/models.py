from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Account(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    name = models.CharField(max_length=100, verbose_name="Название счета")
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name="Баланс")
    card_digits = models.CharField(max_length=4, verbose_name="Последние 4 цифры")
    bank_name = models.CharField(max_length=50, default="Банк", verbose_name="Название банка")

    def __str__(self):
        return f"{self.name} ({self.bank_name})"

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название категории")
    color_code = models.CharField(max_length=7, default="#81c784", verbose_name="Цвет (HEX)")

    def __str__(self):
        return self.name

class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('income', 'Доход'),
        ('expense', 'Расход'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, verbose_name="Счет")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, verbose_name="Категория")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма")
    transaction_type = models.CharField(max_length=7, choices=TRANSACTION_TYPES, verbose_name="Тип")
    date = models.DateField(auto_now_add=True, verbose_name="Дата")

    def __str__(self):
        return f"{self.transaction_type} - {self.amount} ₽"

class Goal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, verbose_name="Цель")
    target_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Целевая сумма")
    current_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Текущая сумма")

    @property
    def percentage(self):
        if self.target_amount > 0:
            return int((self.current_amount / self.target_amount) * 100)
        return 0

    def __str__(self):
        return self.name
