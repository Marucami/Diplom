from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

from .models import (
    Account,
    Category,
    Tag,
    Transaction,
    RecurringTransaction,
    Goal,
    Budget,
    Notification,
    AvailableCategoryTemplate,
)


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name")


class RegisterSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True, validators=[validate_password])

    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User

        fields = (
            "username",
            "email",
            "password",
            "password2",
            "first_name",
            "last_name",
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
            last_name=validated_data.get("last_name", ""),
        )

        return user


class AccountSerializer(serializers.ModelSerializer):
    owner_username = serializers.CharField(source="owner.username", read_only=True)

    # Поля для чтения информации о банке
    bank_name = serializers.CharField(source="bank.name", read_only=True)
    bank_color = serializers.ReadOnlyField(source="bank.color")
    bank_logo = serializers.ReadOnlyField(source="bank.logo_name")

    # Поле для записи ID выбранного банка с фронтенда
    bank_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Account
        # Убираем системное поле 'bank', оставляя явные строковые поля и ID для записи
        fields = [
            "id",
            "name",
            "bank_id",
            "bank_name",
            "bank_color",
            "bank_logo",
            "owner_username",
            "balance",
            "currency",
        ]

        read_only_fields = (
            "owner",
            "owner_username",
            "created_at",
        )

    def create(self, validated_data):
        # Извлекаем bank_id до создания объекта модели
        bank_id = validated_data.pop("bank_id", None)

        request = self.context.get("request")
        if request and request.user and "owner" not in validated_data:
            validated_data["owner"] = request.user

        account = Account.objects.create(**validated_data)

        if bank_id:
            account.bank_id = bank_id
            account.save()

        return account


class CategorySerializer(serializers.ModelSerializer):
    owner_username = serializers.CharField(source="owner.username", read_only=True)
    type_display = serializers.CharField(source="get_type_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    template_color = serializers.SerializerMethodField()
    template_icon = serializers.SerializerMethodField()

    template_id = serializers.IntegerField(
        write_only=True, required=False, allow_null=True
    )

    target_amount = serializers.DecimalField(
        max_digits=12, decimal_places=2, required=False, default=0
    )
    balance = serializers.DecimalField(
        source="total_balance", max_digits=10, decimal_places=2, read_only=True
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
            "template_color",
            "template_icon",
            "template_id",
            "target_amount",
            "deadline",
        )

        read_only_fields = (
            "owner",
            "owner_username",
            "balance",
            "type_display",
            "status_display",
            "created_at",
        )

    def get_template_color(self, obj):
        return obj.template.color_hex if obj.template else "#2c8a93"

    def get_template_icon(self, obj):
        if obj.template:
            return f"/static/icons/{obj.template.icon_name}"
        return "/static/icons/wallet1.png"

    def create(self, validated_data):
        template_id = validated_data.pop("template_id", None)
        target_amount = validated_data.get("target_amount", 0)

        owner = validated_data.pop(
            "owner"
        )  # придёт из serializer.save(owner=request.user)

        category = Category.objects.create(owner=owner, **validated_data)

        if template_id:
            try:
                template = AvailableCategoryTemplate.objects.get(id=template_id)
                category.template = template
                category.save()
            except AvailableCategoryTemplate.DoesNotExist:
                pass

        if category.type == "GL" and target_amount > 0:
            Goal.objects.create(
                name=category.name,
                target_amount=target_amount,
                category=category,
                owner=owner,
            )
        return category


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"
        read_only_fields = ("owner",)


class TransactionCreateSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)

    date = serializers.DateField()

    description = serializers.CharField(required=False, allow_blank=True)

    type = serializers.ChoiceField(choices=Transaction.Type.choices)

    account_id = serializers.IntegerField()

    category_id = serializers.IntegerField(required=False, allow_null=True)


class TransactionSerializer(serializers.ModelSerializer):

    tags = TagSerializer(many=True, read_only=True)

    tag_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        write_only=True,
        source="tags",
        required=False,
    )

    account_id = serializers.PrimaryKeyRelatedField(
        queryset=Account.objects.all(),
        source="account",
        write_only=True,
    )

    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source="category",
        write_only=True,
    )

    account_name = serializers.CharField(
        source="account.name",
        read_only=True,
    )

    category_name = serializers.CharField(
        source="category.name",
        read_only=True,
    )

    class Meta:
        model = Transaction

        fields = (
            "id",
            "amount",
            "date",
            "description",
            "type",
            "account_id",
            "account_name",
            "category_id",
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
        source="category.balance", max_digits=12, decimal_places=2, read_only=True
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


class AvailableCategoryTemplateSerializer(serializers.ModelSerializer):
    icon = serializers.SerializerMethodField()

    class Meta:
        model = AvailableCategoryTemplate
        fields = ["id", "name", "type", "color_hex", "icon"]

    def get_icon(self, obj):
        return f"/static/icons/{obj.icon_name}"


class AnalyticsSerializer(serializers.Serializer):
    expenses = serializers.DictField()
    incomes = serializers.DictField()


class ForecastSerializer(serializers.Serializer):
    predicted_balance = serializers.FloatField(required=False)
    months_to_goal = serializers.IntegerField(required=False)


class MeSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    first_name = serializers.CharField()
