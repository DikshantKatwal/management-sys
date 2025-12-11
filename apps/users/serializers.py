from rest_framework import serializers
from rest_framework import serializers
from django.contrib.auth import authenticate
from apps.customers.serializers import CustomerSerializer
from apps.employees.serializers import EmployeeSerializer
from apps.users.models import User
from rest_framework_simplejwt.tokens import RefreshToken

from apps.customers.models import Customer
from apps.employees.models import Employee
from apps.users.models import User

class EmployeeRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True,required=False)
    # role = serializers.CharField(required=False)
    # department = serializers.CharField(required=False, allow_blank=True)
    # position = serializers.CharField(required=False, allow_blank=True)
    # hire_date = serializers.DateField(required=False)

    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "avatar","password"]

    def create(self, validated_data):
        # role= validated_data.pop("role", Employee.EmployeeRoles.EMPLOYEE)
        # department = validated_data.pop("department", None)
        # position = validated_data.pop("position", None)
        # hire_date = validated_data.pop("hire_date", None)
        password = validated_data.pop("password", None)
        user = User.objects.create_user(
            email=validated_data["email"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            password=password,
            avatar=validated_data["avatar"],
            user_type=User.UserTypes.EMPLOYEE
        )
        # Employee instance after save from signals.py
        # employee:Employee = user.employee_profile
        # employee.role = role
        # employee.department = department
        # employee.position = position
        # employee.hire_date = hire_date
        # employee.save()

        return user
    

class CustomerRegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    password = serializers.CharField(write_only=True)

    phone = serializers.CharField(required=False, allow_blank=True)
    address = serializers.CharField(required=False, allow_blank=True)
    dob = serializers.DateField(required=False)
    loyalty_points = serializers.IntegerField(required=False)

    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "password","phone","address","dob","loyalty_points"]

    def create(self, validated_data):
        customer_data = {
            'phone': validated_data.pop("phone", None),
            'address': validated_data.pop("address", None),
            'dob': validated_data.pop("dob", None),
            'loyalty_points': validated_data.pop("loyalty_points", 10),
        }

        # 1️⃣ Create User
        user = User.objects.create_user(
            email=validated_data["email"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            password=validated_data["password"],
            user_type=User.UserTypes.CUSTOMER
        )

        # 2️⃣ Create Customer with all additional fields
        Customer.objects.create(
            user=user,
            **customer_data
        )

        return user
    

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "last_name","username","avatar","full_name"]




class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        user = authenticate(email=email, password=password)
        if not user:
            raise serializers.ValidationError("Invalid email or password")

        if not user.is_active:
            raise serializers.ValidationError("User account is inactive")

        refresh = RefreshToken.for_user(user)

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "id": str(user.id),
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "role": user.user_type,
            }
        }
    

class UnifiedUserSerializer(serializers.ModelSerializer):
    employee = serializers.SerializerMethodField()
    customer = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "avatar",
            "email",
            "full_name",
            "first_name",
            "last_name",
            "username",
            "user_type",
            "employee",
            "customer",
        ]

    def get_employee(self, obj):
        if hasattr(obj, "employee_profile"):
            return EmployeeSerializer(obj.employee_profile).data
        return None

    def get_customer(self, obj):
        if hasattr(obj, "customer_profile"):
            return CustomerSerializer(obj.customer_profile).data
        return None
