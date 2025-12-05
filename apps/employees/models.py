from apps.common.models import BaseModel
from django.db import models
from apps.users.models import User


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

    def __str__(self):
        return f"{self.user.full_name} ({self.role})"
