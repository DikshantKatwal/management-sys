from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.users.models import User
from apps.employees.models import Employee

@receiver(post_save, sender=User)
def create_profile(sender, instance:User, created, **kwargs):
    if not created:
        return

    if instance.user_type == User.UserTypes.CUSTOMER:
        return

    elif instance.user_type == User.UserTypes.EMPLOYEE:
        Employee.objects.create(
            user=instance,
            role=Employee.EmployeeRoles.EMPLOYEE
        )

    elif instance.user_type == User.UserTypes.ADMIN:
        Employee.objects.create(
            user=instance,
            role=Employee.EmployeeRoles.ADMIN
        )
