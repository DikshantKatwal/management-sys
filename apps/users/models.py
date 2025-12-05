from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)

from apps.common.models import BaseModel


class CustomAccountManager(BaseUserManager):
    def create_superuser(self, email, password, **other_fields):
        other_fields.setdefault("is_staff", True)
        other_fields.setdefault("is_superuser", True)
        other_fields.setdefault("is_active", True)
        other_fields.setdefault("user_type", User.UserTypes.ADMIN)
        
        if other_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must be assigned to is_staff=True"))

        if other_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must be assigned to is_superuser=True"))

        return self.create_user(email, password, **other_fields)

    def create_user(self, email, password=None, **other_fields):
        _first_name = other_fields.pop("first_name", "") or ""
        _last_name = other_fields.pop("last_name", "") or ""
        email = self.normalize_email(email)
        first_name= _first_name.title()
        last_name=_last_name.title()
        user:User = self.model(email=email, first_name=first_name, last_name=last_name, **other_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()
        return user


class User(BaseModel, AbstractBaseUser, PermissionsMixin):
    class UserTypes(models.TextChoices):
        ADMIN = "admin", "Admin"
        CUSTOMER = "customer", "Customer"
        EMPLOYEE = "employee", "Employee"
    email = models.EmailField(_("email address"), unique=True)
    username = models.CharField(max_length=255, null=True, blank=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    auth_provider = models.CharField(max_length=255, null=True, blank=True)
    email_verified = models.BooleanField(default=False, null=True, blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    user_type = models.CharField(
        max_length=20,
        choices=UserTypes.choices,
        default=UserTypes.CUSTOMER
    )
    objects = CustomAccountManager()
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    class Meta:
        db_table = "aauth_user"
