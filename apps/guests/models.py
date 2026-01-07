from apps.common.models import BaseModel
from django.db import models
from apps.users.models import User
from apps.utilities.models import Country,Zone

from django.core.exceptions import ValidationError

class Guest(BaseModel):
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name="guest_profile", null=True)

    address = models.TextField(null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    loyalty_points = models.IntegerField(default=0)
    nationality = models.ForeignKey(Country, on_delete=models.SET_DEFAULT,default=169, null=True)
    province = models.ForeignKey(Zone, on_delete=models.SET_DEFAULT,default=3408, null=True)
    identification = models.CharField(max_length=255, null=True, blank=True)
    id_number = models.CharField(max_length=255, null=True, unique=True)
    
    def __str__(self):
        return self.user.full_name if self.user else "Guest"

    @property
    def full_name(self):
        return self.user.full_name if self.user else ""

    @property
    def avatar(self):
        return self.user.avatar if self.user else None
    
    @property
    def phone(self):
        return self.user.phone if self.user else None
    

    def clean(self):
        """Model-level validation"""
        if self.province and self.nationality:
            if self.province.country_id != self.nationality_id:
                raise ValidationError({
                    "province": "Selected province does not belong to the selected nationality."
                })

    def save(self, *args, **kwargs):
        self.full_clean()  # ensures clean() is called
        return super().save(*args, **kwargs)