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

    password = serializers.CharField(write_only=True,validators=[validate_password])

    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User

        fields = (
            "username",
            "email",
            "password",
            "password2",
            "first_name",
            "last_name"
        )

    def validate(self, attrs):

        if attrs["password"] != attrs["password2"]:

            raise serializers.ValidationError("Пароли не совпадают")

        return attrs

    def create(self, validated_data):

        validated_data.pop("password2")

        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email"),
            password=validated_data["password"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", "")
        )

        return user


class AccountSerializer(serializers.ModelSerializer):

    owner_username = serializers.CharField(
        source="owner.username",
        read_only=True
    )

    class Meta:
        model = Account
        fields = (
            "id",
            "name",
            "balance",
            "currency",
            "owner",
            "owner_username",
            "created_at",
        )

        read_only_fields = (
            "owner",
            "owner_username",
            "created_at",
        )


class CategorySerializer(serializers.ModelSerializer):

    owner_username = serializers.CharField(
        source="owner.username",
        read_only=True
    )

    type_display = serializers.CharField(
        source="get_type_display",
        read_only=True
    )

    status_display = serializers.CharField(
        source="get_status_display",
        read_only=True
    )

    class Meta:
        model = Category
        fields = (
            "id",
            "name",
            "type",
            "type_display",
            "balance",
            "status",
            "status_display",
            "owner",
            "owner_username",
            "created_at",
        )

        read_only_fields = (
            "owner",
            "owner_username",
            "balance",
            "type_display",
            "status_display",
            "created_at",
        )


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

    category_name = serializers.CharField(
        source='category.name',
        read_only=True
    )

    account_name = serializers.CharField(
        source='account.name',
        read_only=True
    )

    class Meta:
        model = Transaction
        fields = (
            "id",
            "amount",
            "date",
            "description",
            "type",
            "account",
            "account_name",
            "category",
            "category_name",
            "tags",
            "tag_ids",
            "owner",
            "created_at",
        )

        read_only_fields = (
            "owner",
            "created_at",
            "account_name",
            "category_name",
        )

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