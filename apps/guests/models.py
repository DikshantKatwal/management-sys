from apps.common.models import BaseModel
from django.db import models
from apps.users.models import User


class Guest(BaseModel):
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name="guest_profile", null=True)

    address = models.TextField(null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    loyalty_points = models.IntegerField(default=0)

    nationality = models.CharField(max_length=255, null=True, blank=True)
    identification = models.CharField(max_length=255, null=True, blank=True)
    id_number = models.CharField(max_length=255, null=True, unique=True)

    def __str__(self):
        return self.user.full_name
