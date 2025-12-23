from rest_framework import serializers
from decimal import Decimal
from django.db.models import Sum

from .models import (
    Reservation, Stay, StayExtension,
    Folio, Charge, Payment, FolioAdjustment,
    MenuItem, FoodOrder, FoodOrderItem
)
from django.db import models

# ---------- Reservation ----------

exclude_fields = ["restored_at", "deleted_at", "transaction_id","updated_at"]
class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        # exclude = exclude_fields
        exclude = exclude_fields

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["guest_name"] = instance.guest.full_name
        return representation

# ---------- Stay ----------

class StayExtensionSerializer(serializers.ModelSerializer):
    class Meta:
        model = StayExtension
        exclude = exclude_fields


class StaySerializer(serializers.ModelSerializer):
    extensions = StayExtensionSerializer(many=True, read_only=True)

    class Meta:
        model = Stay
        exclude = exclude_fields


# ---------- Billing ----------

class ChargeSerializer(serializers.ModelSerializer):
    subtotal = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True
    )
    total = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True
    )

    class Meta:
        model = Charge
        exclude = exclude_fields


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        exclude = exclude_fields


    def validate(self, attrs):
        user = self.context["request"].user
        if hasattr(user, "employee_profile"):
            attrs["created_by"] = user.employee_profile
        return super().validate(attrs)


class FolioAdjustmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = FolioAdjustment
        exclude = exclude_fields


class FolioSerializer(serializers.ModelSerializer):
    charges = ChargeSerializer(many=True, read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)
    adjustments = FolioAdjustmentSerializer(many=True, read_only=True)

    total_charges = serializers.SerializerMethodField()
    total_payments = serializers.SerializerMethodField()
    total_adjustments = serializers.SerializerMethodField()
    balance = serializers.SerializerMethodField()

    class Meta:
        model = Folio
        exclude = exclude_fields

    def get_total_charges(self, obj):
        return obj.charges.aggregate(
            total=Sum(
                (models.F("quantity") * models.F("unit_price")) +
                models.F("tax_amount") -
                models.F("discount_amount")
            )
        )["total"] or Decimal("0.00")

    def get_total_payments(self, obj):
        return obj.payments.aggregate(
            total=Sum("amount")
        )["total"] or Decimal("0.00")

    def get_total_adjustments(self, obj):
        return obj.adjustments.aggregate(
            total=Sum("amount")
        )["total"] or Decimal("0.00")

    def get_balance(self, obj):
        return (
            self.get_total_charges(obj)
            + self.get_total_adjustments(obj)
            - self.get_total_payments(obj)
        )


# ---------- Menu & Food ----------

class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        exclude = exclude_fields


class FoodOrderItemSerializer(serializers.ModelSerializer):
    line_total = serializers.SerializerMethodField()

    class Meta:
        model = FoodOrderItem
        exclude = exclude_fields

    def get_line_total(self, obj):
        return obj.quantity * obj.unit_price


class FoodOrderSerializer(serializers.ModelSerializer):
    items = FoodOrderItemSerializer(many=True, read_only=True)
    formatted_order_number = serializers.CharField(read_only=True)

    order_total = serializers.SerializerMethodField()

    class Meta:
        model = FoodOrder
        exclude = exclude_fields

    def get_order_total(self, obj):
        return sum(
            (item.quantity * item.unit_price)
            for item in obj.items.all()
        )
