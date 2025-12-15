# from django.db import models

# from apps.common.models import BaseModel
# from apps.guests.models import guest
# from apps.rooms.models import Room
# from apps.users.models import User
# # Create your models here.


# class CheckIn(BaseModel):
#     guest = models.ForeignKey(guest, null=True, blank=True, on_delete=models.CASCADE)
#     room = models.ForeignKey(Room, null=True, blank=True, on_delete=models.CASCADE)

#     total_people = models.IntegerField(null=True, blank=True)
#     male_count = models.IntegerField(null=True, blank=True)
#     female_count = models.IntegerField(null=True, blank=True)
#     check_in_date = models.DateField(null=True, blank=True)
#     check_in_time = models.TimeField(null=True, blank=True)

#     gross_rate = models.IntegerField(null=True, blank=True)
#     discount = models.IntegerField(null=True, blank=True)

#     check_out = models.BooleanField(null=True, blank=True, default=False)
#     check_out_date = models.DateField(null=True, blank=True)
#     check_out_time = models.TimeField(null=True, blank=True)

#     total_days = models.IntegerField(null=True, blank=True)

#     total_paid = models.IntegerField(null=True, blank=True)

   

# class Payment(BaseModel):
#     checkin = models.ForeignKey(CheckIn, null=True, blank=True, on_delete=models.CASCADE,
#                                 related_name='payments')
#     agreed_price = models.IntegerField(null=True, blank=True)
    
#     amount_paid = models.IntegerField(null=True, blank=True)

#     payment_on = models.DateTimeField(auto_now_add=True)
#     created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE,
#                                    related_name='payment_by')



# class CheckInHistory(BaseModel):
#     guest = models.ForeignKey(guest, null=True, blank=True, on_delete=models.CASCADE)
#     room = models.ForeignKey(Room, null=True, blank=True, on_delete=models.CASCADE)
#     agreed_price = models.IntegerField(null=True, blank=True)
#     discount = models.IntegerField(null=True, blank=True)
#     advance = models.IntegerField(null=True, blank=True)
#     total_people = models.IntegerField(null=True, blank=True)
#     male_count = models.IntegerField(null=True, blank=True)
#     female_count = models.IntegerField(null=True, blank=True)
#     check_in_date = models.DateField(null=True, blank=True)
#     check_in_time = models.TimeField(null=True, blank=True)






# from django.db import models
# from django.conf import settings
# from django.utils import timezone
# from decimal import Decimal
# import uuid



# # ---------- Guests / guests ----------

# class Guest(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     full_name = models.CharField(max_length=200)
#     phone = models.CharField(max_length=40, blank=True)
#     email = models.EmailField(blank=True)
#     id_number = models.CharField(max_length=100, blank=True)  # passport/citizenship/etc.
#     address = models.TextField(blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.full_name


# # ---------- Reservation / Stay (Check-in/Check-out) ----------

from apps.common.models import BaseModel
from django.db import models

from apps.guests.models import Guest
from apps.rooms.models import Room, RoomType
from django.utils import timezone


class Reservation(BaseModel):
    class Status(models.TextChoices):
        HOLD = "hold", "Hold"
        CONFIRMED = "confirmed", "Confirmed"
        CHECKED_IN = "checked_in", "Checked In"
        CHECKED_OUT = "checked_out", "Checked Out"
        CANCELLED = "cancelled", "Cancelled"
        NO_SHOW = "no_show", "No show"

    guest = models.ForeignKey(Guest, on_delete=models.PROTECT, related_name="reservations")

    # If you assign a specific room at booking time (optional)
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

# class Folio(models.Model):
#     """
#     One folio per stay (or multiple if you want split billing later).
#     All charges & payments go here.
#     """
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     stay = models.OneToOneField(Stay, on_delete=models.CASCADE, related_name="folio")
#     currency = models.CharField(max_length=10, default="NPR")
#     is_closed = models.BooleanField(default=False)
#     created_at = models.DateTimeField(auto_now_add=True)


# class Charge(models.Model):
#     """
#     Any billable item: room night, food, minibar, laundry, extra bed, etc.
#     """
#     class Category(models.TextChoices):
#         ROOM = "room", "Room"
#         FOOD = "food", "Food"
#         SERVICE = "service", "Service"
#         OTHER = "other", "Other"

#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     folio = models.ForeignKey(Folio, on_delete=models.CASCADE, related_name="charges")
#     category = models.CharField(max_length=20, choices=Category.choices)
#     description = models.CharField(max_length=255)

#     quantity = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("1.00"))
#     unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
#     tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
#     discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))

#     occurred_at = models.DateTimeField(default=timezone.now)  # when service consumed
#     posted_at = models.DateTimeField(auto_now_add=True)      # when added to folio

#     created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

#     @property
#     def subtotal(self):
#         return (self.quantity * self.unit_price)

#     @property
#     def total(self):
#         return (self.subtotal + self.tax_amount - self.discount_amount)


# class Payment(models.Model):
#     class Method(models.TextChoices):
#         CASH = "cash", "Cash"
#         CARD = "card", "Card"
#         BANK = "bank", "Bank Transfer"
#         MOBILE = "mobile", "Mobile Wallet"
#         OTHER = "other", "Other"

#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     folio = models.ForeignKey(Folio, on_delete=models.CASCADE, related_name="payments")
#     method = models.CharField(max_length=20, choices=Method.choices)
#     amount = models.DecimalField(max_digits=12, decimal_places=2)
#     reference = models.CharField(max_length=120, blank=True)  # txn id / receipt no
#     received_at = models.DateTimeField(default=timezone.now)

#     is_advance = models.BooleanField(default=False)  # advance payment before checkout
#     created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)


# class FolioAdjustment(models.Model):
#     """
#     For global discounts or manual adjustments that aren't tied to one charge line.
#     Keeps audit trail clean.
#     """
#     class Type(models.TextChoices):
#         DISCOUNT = "discount", "Discount"
#         SURCHARGE = "surcharge", "Surcharge"
#         CORRECTION = "correction", "Correction"

#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     folio = models.ForeignKey(Folio, on_delete=models.CASCADE, related_name="adjustments")
#     type = models.CharField(max_length=20, choices=Type.choices)
#     description = models.CharField(max_length=255, blank=True)
#     amount = models.DecimalField(max_digits=12, decimal_places=2)  # discount as positive number
#     created_at = models.DateTimeField(auto_now_add=True)
#     created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)


# # ---------- Food / Room service ----------

# class MenuItem(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name="menu_items")
#     name = models.CharField(max_length=200)
#     price = models.DecimalField(max_digits=12, decimal_places=2)
#     is_active = models.BooleanField(default=True)

#     class Meta:
#         unique_together = ("hotel", "name")


# class FoodOrder(models.Model):
#     """
#     An order placed during a stay. Posting to folio can be immediate or when delivered.
#     """
#     class Status(models.TextChoices):
#         PLACED = "placed", "Placed"
#         PREPARING = "preparing", "Preparing"
#         DELIVERED = "delivered", "Delivered"
#         CANCELLED = "cancelled", "Cancelled"

#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     stay = models.ForeignKey(Stay, on_delete=models.CASCADE, related_name="food_orders")
#     status = models.CharField(max_length=20, choices=Status.choices, default=Status.PLACED)
#     notes = models.TextField(blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)


# class FoodOrderItem(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     order = models.ForeignKey(FoodOrder, on_delete=models.CASCADE, related_name="items")
#     menu_item = models.ForeignKey(MenuItem, on_delete=models.PROTECT)
#     quantity = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("1.00"))
#     unit_price = models.DecimalField(max_digits=12, decimal_places=2)  # snapshot price at time of order

#     def line_total(self):
#         return self.quantity * self.unit_price
