from apps.common.models import BaseModel
from django.db import models
from apps.users.models import User



class Room(BaseModel):
    class RoomType(models.TextChoices):
        DELUX = "deluxe", "Deluxe"
        STANDARD = "standard", "Standard"

    class RoomStatus(models.TextChoices):
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "In-Active"
        BOOKED = "booked", "Booked"
        DIRTY = "dirty", "Dirty"

    name = models.CharField(max_length=100)
    type = models.CharField(
        max_length=20,
        choices=RoomType.choices,
        default=RoomType.STANDARD
    )
    sequence = models.IntegerField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=RoomStatus.choices,
        default=RoomStatus.ACTIVE
    )

    def save(self, *args, **kwargs):
        if self.sequence is None:
            last_room = Room.objects.order_by('-sequence').first()
            self.sequence = (last_room.sequence + 1) if last_room else 1

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.type})"



