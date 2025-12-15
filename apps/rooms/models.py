from apps.common.models import BaseModel
from django.db import models
from decimal import Decimal

class RoomType(BaseModel):
    name = models.CharField(max_length=120)  # Deluxe, Suite, etc.
    max_occupancy = models.PositiveSmallIntegerField(default=2)
    base_rate = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name}"


class Room(BaseModel):
    class Status(models.TextChoices):
        AVAILABLE = "available", "Available"
        OCCUPIED = "occupied", "Occupied"
        OUT_OF_ORDER = "out_of_order", "Out of order"
        CLEANING = "cleaning", "Cleaning"

    room_type = models.ForeignKey(RoomType, on_delete=models.PROTECT, related_name="rooms")
    number = models.CharField(max_length=20)  # 101, A-12, etc.
    floor = models.CharField(max_length=20, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.AVAILABLE)
    sequence = models.IntegerField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.sequence is None:
            last_room = Room.objects.order_by('-sequence').first() or 0
            self.sequence = (last_room.sequence or 0) + 1 if last_room else 1

        super().save(*args, **kwargs)

    def __str__(self):
        return f" #{self.number}"
