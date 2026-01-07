from apps.common.models import BaseModel
from django.db import models
from apps.users.models import User
from apps.utilities.models import Country, Zone
from django.core.exceptions import ValidationError


class Employee(BaseModel):
    class EmployeeRoles(models.TextChoices):
        ADMIN = "admin", "Admin"
        EMPLOYEE = "employee", "Employee"
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="employee_profile"
    )
    role = models.CharField(
        max_length=20,
        choices=EmployeeRoles.choices,
        default=EmployeeRoles.EMPLOYEE
    )
    department = models.CharField(max_length=255, null=True, blank=True)
    position = models.CharField(max_length=255, null=True, blank=True)
    hire_date = models.DateField(null=True, blank=True)

    country = models.ForeignKey(
        Country,
        on_delete=models.PROTECT,
        related_name="employee_addresses",
        default=169
    )

    province = models.ForeignKey(
        Zone,
        on_delete=models.PROTECT,
        default=3408,
        related_name="employee_addresses",
    )

    city = models.CharField(max_length=100,default="not-specified")
    address_line_1 = models.CharField(max_length=255,null=True, blank=True)
    address_line_2 = models.CharField(max_length=255,null=True, blank=True)

    postal_code = models.CharField(max_length=20, null=True, blank=True)


    def __str__(self):
        return f"{self.user.full_name} ({self.role})"

    def clean(self):
        """Model-level validation"""
        if self.province and self.country:
            if self.province.country_id != self.country_id:
                raise ValidationError({
                    "province": "Selected province does not belong to the selected country."
                })

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)