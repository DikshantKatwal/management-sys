from rest_framework import serializers
from rest_framework import serializers
from django.contrib.auth import authenticate
from apps.employees.serializers import EmployeeSerializer
from apps.guests.serializers import GuestSerializer
from apps.users.models import User
from rest_framework_simplejwt.tokens import RefreshToken

from apps.guests.models import Guest
from apps.users.models import User

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True,required=False)

    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "username","avatar","phone", "password"]

    def create(self, validated_data):
        print(validated_data)
        user = User.objects.create_user(**validated_data
        )
        return user
    

class GuestRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "avatar","phone"]

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data["email"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            password=validated_data["password"],
            user_type=User.UserTypes.GUEST
        )
        return user
    

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "last_name","username","phone","avatar","email","full_name","user_type"]




class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")
        user:User = authenticate(
            username=username,
            password=password
        )
        if not user:
            raise serializers.ValidationError("Invalid phone or password")

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
    guest = serializers.SerializerMethodField()
    guest_id = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "guest_id",
            "avatar",
            "email",
            "phone",
            "full_name",
            "first_name",
            "last_name",
            "username",
            "user_type",
            "employee",
            "guest",
        ]

    def get_employee(self, obj):
        if hasattr(obj, "employee_profile"):
            return EmployeeSerializer(obj.employee_profile).data
        return None
    
    def get_guest(self, obj):
        if hasattr(obj, "guest_profile"):
            return GuestSerializer(obj.guest_profile).data
        return None
    
    def get_guest_id(self, obj):
        if hasattr(obj, "guest_profile"):
            return obj.guest_profile.id
        return None