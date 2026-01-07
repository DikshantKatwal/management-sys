
from django.forms import ValidationError
from apps.common.models import BaseModel
from django.db import models,transaction

from apps.employees.models import Employee
from apps.guests.models import Guest
from apps.rooms.models import Room, RoomType
from django.utils import timezone
from decimal import Decimal
from django.db.models import Max


class Reservation(BaseModel):
    class Status(models.TextChoices):
        HOLD = "hold", "Hold"
        CONFIRMED = "confirmed", "Confirmed"
        CHECKED_IN = "checked_in", "Checked In"
        CHECKED_OUT = "checked_out", "Checked Out"
        CANCELLED = "cancelled", "Cancelled"
        NO_SHOW = "no_show", "No show"

    guest = models.ForeignKey(Guest, on_delete=models.PROTECT, related_name="reservations")

    room = models.ForeignKey(Room, on_delete=models.PROTECT, null=True, blank=True, related_name="reservations")
    room_type = models.ForeignKey(RoomType, on_delete=models.PROTECT, null=True, blank=True, related_name="reservations")

    check_in_date = models.DateField()
    check_out_date = models.DateField()

    adults = models.PositiveSmallIntegerField(default=1)
    children = models.PositiveSmallIntegerField(default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.CONFIRMED)
    notes = models.TextField(blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["check_in_date", "check_out_date"]),
        ]

    def __str__(self):
        return f"{self.guest} {self.check_in_date}→{self.check_out_date}"


class Stay(BaseModel):
    """
    Operational record created at check-in. Reservation can exist without stay.
    """
    class Status(models.TextChoices):
        IN_HOUSE = "in_house", "In house"
        CHECKED_OUT = "checked_out", "Checked out"

    reservation = models.OneToOneField(Reservation, on_delete=models.PROTECT, related_name="stay")
    room = models.ForeignKey(Room, on_delete=models.PROTECT, related_name="stays")

    checked_in_at = models.DateTimeField(default=timezone.now)
    checked_out_at = models.DateTimeField(null=True, blank=True)

    expected_check_out_date = models.DateField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.IN_HOUSE)

    def __str__(self):
        return f"Stay {self.id} ({self.room})"


class StayExtension(BaseModel):
    """
    Every time guest adds days, store it as an extension record.
    (Audit-friendly and scalable.)
    """
    stay = models.ForeignKey(Stay, on_delete=models.CASCADE, related_name="extensions")
    old_check_out_date = models.DateField()
    new_check_out_date = models.DateField()
    reason = models.CharField(max_length=255, blank=True)

    class Meta:
        indexes = [models.Index(fields=["stay", "created_at"])]


# # ---------- Billing (Folio/Ledger) ----------
from django.db.models import Sum, F
from decimal import Decimal

class Folio(BaseModel):
    """
    One folio per stay (or multiple if you want split billing later).
    All charges & payments go here.
    """
    stay = models.OneToOneField(Stay, on_delete=models.CASCADE, related_name="folio")
    currency = models.CharField(max_length=10, default="NPR")
    is_closed = models.BooleanField(default=False)

    @property
    def total_charges(self):
        return self.charges.aggregate(
            total=Sum(
                (F("quantity") * F("unit_price")) +
                F("tax_amount") -
                F("discount_amount")
            )
        )["total"] or Decimal("0.00")
    
    @property
    def total_payments(self):
        return self.payments.aggregate(
            total=Sum("amount")
        )["total"] or Decimal("0.00")

    @property
    def total_adjustments(self):
        return self.adjustments.aggregate(
            total=Sum("amount")
        )["total"] or Decimal("0.00")

    @property
    def balance(self):
        return self.total_charges + self.total_adjustments - self.total_payments

    def is_balanced(self):
        return self.balance == Decimal("0.00")


class Charge(BaseModel):
    """
    Any billable item: room night, food, minibar, laundry, extra bed, etc.
    """
    class Category(models.TextChoices):
        ROOM = "room", "Room"
        FOOD = "food", "Food"
        SERVICE = "service", "Service"
        OTHER = "other", "Other"

    folio = models.ForeignKey(Folio, on_delete=models.CASCADE, related_name="charges")
    category = models.CharField(max_length=20, choices=Category.choices)
    description = models.CharField(max_length=255)

    quantity = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("1.00"))
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    occurred_at = models.DateTimeField(default=timezone.now)
    posted_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True)

    @property
    def subtotal(self):
        return (self.quantity * self.unit_price)

    @property
    def total(self):
        return (self.subtotal + self.tax_amount - self.discount_amount)


class Payment(BaseModel):
    class Method(models.TextChoices):
        CASH = "cash", "Cash"
        CARD = "card", "Card"
        BANK = "bank", "Bank Transfer"
        MOBILE = "mobile", "Mobile Wallet"
        OTHER = "other", "Other"

    folio = models.ForeignKey(Folio, on_delete=models.CASCADE, related_name="payments")
    method = models.CharField(max_length=20, choices=Method.choices)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    reference = models.CharField(max_length=120, blank=True)
    received_at = models.DateTimeField(default=timezone.now)

    is_advance = models.BooleanField(default=False)
    created_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True)


class FolioAdjustment(BaseModel):
    """
    For global discounts or manual adjustments that aren't tied to one charge line.
    Keeps audit trail clean.
    """
    class Type(models.TextChoices):
        DISCOUNT = "discount", "Discount"
        SURCHARGE = "surcharge", "Surcharge"
        CORRECTION = "correction", "Correction"

    folio = models.ForeignKey(Folio, on_delete=models.CASCADE, related_name="adjustments")
    type = models.CharField(max_length=20, choices=Type.choices)
    description = models.CharField(max_length=255, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2) 
    created_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True)


# # ---------- Food / Room service ----------

class MenuItem(BaseModel):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    is_active = models.BooleanField(default=True)


class FoodOrder(BaseModel):
    """
    An order placed during a stay. Posting to folio can be immediate or when delivered.
    """
    class Status(models.TextChoices):
        PLACED = "placed", "Placed"
        PREPARING = "preparing", "Preparing"
        DELIVERED = "delivered", "Delivered"
        CANCELLED = "cancelled", "Cancelled"

    stay = models.ForeignKey(Stay, on_delete=models.CASCADE, related_name="food_orders")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PLACED)
    order_number = models.PositiveIntegerField(
        unique=True,
        editable=False,
        null=True,
        blank=True
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.order_number is None:
            with transaction.atomic():
                last = FoodOrder.objects.select_for_update().aggregate(
                    max_num=Max("order_number")
                )["max_num"]
                self.order_number = (last or 0) + 1
        super().save(*args, **kwargs)

    @property
    def formatted_order_number(self):
        return f"{self.order_number:04d}"


class FoodOrderItem(BaseModel):
    order = models.ForeignKey(FoodOrder, on_delete=models.CASCADE, related_name="items")
    menu_item = models.ForeignKey(MenuItem, on_delete=models.PROTECT)
    quantity = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("1.00"))
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)  # snapshot price at time of order

    def line_total(self):
        return self.quantity * self.unit_price

    def save(self, *args, **kwargs):
        if self.pk and self.order.status == FoodOrder.Status.DELIVERED:
            raise ValidationError("Cannot modify delivered order")
        super().save(*args, **kwargs)