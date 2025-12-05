from django.db import models

from apps.common.models import BaseModel
from apps.customers.models import Customer
from apps.rooms.models import Room
from apps.users.models import User
# Create your models here.


class CheckIn(BaseModel):
    customer = models.ForeignKey(Customer, null=True, blank=True, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, null=True, blank=True, on_delete=models.CASCADE)

    total_people = models.IntegerField(null=True, blank=True)
    male_count = models.IntegerField(null=True, blank=True)
    female_count = models.IntegerField(null=True, blank=True)
    check_in_date = models.DateField(null=True, blank=True)
    check_in_time = models.TimeField(null=True, blank=True)

    gross_rate = models.IntegerField(null=True, blank=True)
    discount = models.IntegerField(null=True, blank=True)

    check_out = models.BooleanField(null=True, blank=True, default=False)
    check_out_date = models.DateField(null=True, blank=True)
    check_out_time = models.TimeField(null=True, blank=True)

    total_days = models.IntegerField(null=True, blank=True)

    total_paid = models.IntegerField(null=True, blank=True)

   

class Payment(BaseModel):
    checkin = models.ForeignKey(CheckIn, null=True, blank=True, on_delete=models.CASCADE,
                                related_name='payments')
    agreed_price = models.IntegerField(null=True, blank=True)
    
    amount_paid = models.IntegerField(null=True, blank=True)

    payment_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE,
                                   related_name='payment_by')



class CheckInHistory(BaseModel):
    customer = models.ForeignKey(Customer, null=True, blank=True, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, null=True, blank=True, on_delete=models.CASCADE)
    agreed_price = models.IntegerField(null=True, blank=True)
    discount = models.IntegerField(null=True, blank=True)
    advance = models.IntegerField(null=True, blank=True)
    total_people = models.IntegerField(null=True, blank=True)
    male_count = models.IntegerField(null=True, blank=True)
    female_count = models.IntegerField(null=True, blank=True)
    check_in_date = models.DateField(null=True, blank=True)
    check_in_time = models.TimeField(null=True, blank=True)
