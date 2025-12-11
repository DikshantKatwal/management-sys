from rest_framework import status,generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from apps.common.permissions import IsAdminUser
from apps.customers.serializers import CustomerSerializer
from apps.employees.serializers import EmployeeSerializer
from apps.users.models import User
from .serializers import (
    CustomerRegisterSerializer,
    EmployeeRegisterSerializer,
    LoginSerializer,
    UnifiedUserSerializer,
    UserSerializer,
)
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from django.db import transaction

class CustomerRegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = CustomerRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {"message": "Customer registered successfully", "id": str(user.id)},
            status=status.HTTP_201_CREATED
        )


class EmployeeRegisterView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = EmployeeSerializer

    @transaction.atomic
    def post(self, request):
        data = request.data
        serializer = EmployeeRegisterSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        user:User = serializer.save()
        if hasattr(user, "employee_profile"):
            employee = user.employee_profile
            employee_serializer = self.get_serializer(instance=employee, data=data)
            employee_serializer.is_valid(raise_exception=True)
            employee_serializer.save()
        return Response(
            employee_serializer.data,
            status=status.HTTP_201_CREATED
        )





class CookieTokenRefreshView(APIView):
    authentication_classes = []   # no auth required
    permission_classes = []

    def post(self, request):
        refresh_token = request.COOKIES.get("refresh")

        if not refresh_token:
            return Response(
                {"detail": "Refresh token not found"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)

        except TokenError:
            return Response(
                {"detail": "Invalid or expired refresh token"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        response = Response(
            {"detail": "Token refreshed"},
            status=status.HTTP_200_OK,
        )

        response.set_cookie(
            key="access",
            value=access_token,
            httponly=True,
            secure=False,      # True in production (HTTPS)
            samesite="Lax",
            path="/",
            max_age=3600,
            domain="localhost",  # remove in prod
        )

        return response
    
class LoginView(APIView):
    permission_classes=[AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        refresh = data.pop("refresh")
        user = data.pop("user")
        access = data.pop("access")
        response = Response(user, status=status.HTTP_200_OK)
        response.set_cookie(
            "access",
            access,
            httponly=True,
            secure=False,
            samesite="Lax",
            path="/",
            max_age=3600,         # 👈 critical
        )

        response.set_cookie(
            "refresh",
            refresh,
            httponly=True,
            secure=False,
            samesite="Lax",
            path="/",
            max_age=86400,
        )

        return response


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logged out successfully"}, status=200)
        except Exception:
            return Response({"error": "Invalid refresh token"}, status=400)
        
        
class UserAPIView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UnifiedUserSerializer

    def get(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @transaction.atomic
    def put(self, request):
        user:User = request.user
        data = request.data.copy()
        if request.FILES.get('avatar'):
            data['avatar'] = request.FILES.get('avatar')
            user.avatar.delete(save=False)
        user_serializer = UserSerializer(user, data=data, partial=True)
        user_serializer.is_valid(raise_exception=True)
        user_serializer.save()

        # Update employee/customer profile
        if hasattr(user, "employee_profile"):
            employee = user.employee_profile
            emp_serializer = EmployeeSerializer(employee, data=data, partial=True)
            emp_serializer.is_valid(raise_exception=True)
            emp_serializer.save()

        if hasattr(user, "customer_profile"):
            customer = user.customer_profile
            cus_serializer = CustomerSerializer(customer, data=data, partial=True)
            cus_serializer.is_valid(raise_exception=True)
            cus_serializer.save()

        serializer = UnifiedUserSerializer(user)
        return Response(serializer.data)