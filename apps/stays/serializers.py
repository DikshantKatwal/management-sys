from rest_framework import serializers
from decimal import Decimal
from django.db.models import Sum

from apps.guests.models import Guest
from apps.guests.serializers import GuestUserSerializer
from apps.rooms.models import Room, RoomType
from apps.rooms.serializers import RoomSerializer, RoomTypeSerializer

from .models import (
    Reservation, Stay, StayExtension,
    Folio, Charge, Payment, FolioAdjustment,
    MenuItem, FoodOrder, FoodOrderItem
)
from django.db import models
from django.db import transaction


# ---------- Reservation ----------

exclude_fields = ["restored_at", "deleted_at", "transaction_id","updated_at"]
class ReservationSerializer(serializers.ModelSerializer):
    guest = GuestUserSerializer(read_only=True)

    guest_id = serializers.PrimaryKeyRelatedField(
        queryset=Guest.objects.all(),
        source="guest",
        write_only=True
    )

    room = RoomSerializer(read_only=True)

    room_id = serializers.PrimaryKeyRelatedField(
        queryset=Room.objects.all(),
        source="room",
        write_only=True,
        required=False,
        allow_null=True,
    )

    room_type = RoomTypeSerializer(read_only=True)

    room_type_id = serializers.PrimaryKeyRelatedField(
        queryset=RoomType.objects.all(),
        source="room_type",
        write_only=True,
        required=False,
        allow_null=True,

    )
    def validate(self, attrs):
        check_in = attrs.get("check_in_date")
        check_out = attrs.get("check_out_date")
        if check_in and check_out:
            if check_in >= check_out:
                raise serializers.ValidationError({
                    "check_out_date": "Check-out date must be after check-in date."
                })

        return super().validate(attrs)
    
    class Meta:
        model = Reservation
        exclude = exclude_fields


# ---------- Stay ----------

class StayExtensionSerializer(serializers.ModelSerializer):
    class Meta:
        model = StayExtension
        exclude = exclude_fields


class StaySerializer(serializers.ModelSerializer):
    reservation = ReservationSerializer(read_only=True)

    reservation_id = serializers.PrimaryKeyRelatedField(
        queryset=Reservation.objects.all(),
        source="reservation",
        write_only=True
    )

    room = RoomSerializer(read_only=True)

    room_id = serializers.PrimaryKeyRelatedField(
        queryset=Room.objects.all(),
        source="room",
        write_only=True
    )

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


class FoodOrderItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodOrderItem
        fields = ["menu_item", "quantity"]


class FoodOrderCreateSerializer(serializers.ModelSerializer):
    items = FoodOrderItemCreateSerializer(many=True)

    class Meta:
        model = FoodOrder
        fields = ["stay", "notes", "items"]

    def validate_items(self, items):
        if not items:
            raise serializers.ValidationError("Order must contain at least one item")
        return items

    def create(self, validated_data):
        items_data = validated_data.pop("items")

        with transaction.atomic():
            order = FoodOrder.objects.create(**validated_data)

            for item in items_data:
                menu_item = item["menu_item"]
                FoodOrderItem.objects.create(
                    order=order,
                    menu_item=menu_item,
                    quantity=item.get("quantity", Decimal("1.00")),
                    unit_price=menu_item.price,  # snapshot price
                )

        return order