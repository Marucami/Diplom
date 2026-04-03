from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

from .models import (
    Account, Category, Tag,
    Transaction, RecurringTransaction,
    Goal, Budget, Notification
)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name")


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("username", "email", "password", "password2", "first_name", "last_name")

    def validate(self, data):
        if data.get("password") != data.get("password2"):
            raise serializers.ValidationError("Пароли не совпадают")
        return data

    def create(self, data):
        user = User(
            username=data["username"],
            email=data["email"],
            first_name=data.get("first_name", ""),
            last_name=data.get("last_name", "")
        )
        user.set_password(data["password"])
        user.save()
        return user


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = "__all__"
        read_only_fields = ("owner",)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"
        read_only_fields = ("owner", "balance")


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"
        read_only_fields = ("owner",)


class TransactionSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        write_only=True,
        source="tags",
        required=False
    )

    class Meta:
        model = Transaction
        fields = "__all__"
        read_only_fields = ("owner",)

    def validate(self, data):
        user = self.context["request"].user

        account = data.get("account")
        category = data.get("category")
        tags = data.get("tags", [])

        if account and account.owner != user:
            raise serializers.ValidationError("Этот счёт не твой")

        if category and category.owner != user:
            raise serializers.ValidationError("Категория не твоя")

        for tag in tags:
            if tag.owner != user:
                raise serializers.ValidationError(f"Тег '{tag.name}' чужой")

        return data


class RecurringTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecurringTransaction
        fields = "__all__"
        read_only_fields = ("owner",)

    def validate(self, data):
        user = self.context["request"].user

        if data["account"].owner != user:
            raise serializers.ValidationError("Этот счёт не твой")

        category = data.get("category")
        if category and category.owner != user:
            raise serializers.ValidationError("Категория не твоя")

        return data


class GoalSerializer(serializers.ModelSerializer):
    current_amount = serializers.DecimalField(
        source="category.balance",
        max_digits=12,
        decimal_places=2,
        read_only=True
    )
    progress_percent = serializers.IntegerField(read_only=True)

    class Meta:
        model = Goal
        fields = "__all__"
        read_only_fields = ("owner", "current_amount", "progress_percent")

    def validate(self, data):
        user = self.context["request"].user

        if data["category"].owner != user:
            raise serializers.ValidationError("Категория не твоя")

        return data


class BudgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Budget
        fields = "__all__"
        read_only_fields = ("owner",)

    def validate(self, data):
        user = self.context["request"].user

        if data["category"].owner != user:
            raise serializers.ValidationError("Категория не твоя")

        return data


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = "__all__"
        read_only_fields = ("user",)