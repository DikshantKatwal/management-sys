from rest_framework import status,generics,viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from apps.common.permissions import IsAdminUser
from apps.guests.models import Guest
from apps.guests.serializers import GuestSerializer
from apps.employees.models import Employee
from apps.employees.serializers import EmployeeSerializer
from apps.users.models import User
from .serializers import (
    UserRegisterSerializer,
    LoginSerializer,
    UnifiedUserSerializer,
    UserSerializer,
)
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.db import transaction
from django.db.models import Q
from rest_framework.exceptions import ValidationError

import logging
logger = logging.getLogger(__name__)


class GuestRegisterView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = GuestSerializer
    queryset = User.objects.all()
    http_method_names =["put","post"]
    lookup_field="id"
    lookup_url_kwarg ="id"

    @transaction.atomic
    def create(self, request):
        try:
            with transaction.atomic():
                data = request.data
                phone = data.get("phone")
                email = data.get("email")
                if User.objects.filter(
                    Q(phone=phone) | Q(email__iexact=email)
                ).exists():
                    raise ValidationError({"phone": "This phone already exists"})
                
                serializer = UserRegisterSerializer(data=data)
                serializer.is_valid(raise_exception=True)
                user:User = serializer.save(user_type=User.UserTypes.GUEST)
                if hasattr(user, "guest_profile"):
                    guest = user.guest_profile
                    guest_serializer = self.get_serializer(guest, data=data)
                    guest_serializer.is_valid(raise_exception=True)
                    guest_serializer.save()
                    return Response(
                        guest_serializer.data,
                        status=status.HTTP_201_CREATED
                    )
                return Response("guest profile not found", status= status.HTTP_404_NOT_FOUND)

        except Exception as e:
            print(e)
            return Response(str(e), status= status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @transaction.atomic
    def update(self, request, *args, **kwargs):
        try:
            data = request.data
            user = self.get_object()
            if request.FILES.get('avatar'):
                data['avatar'] = request.FILES.get('avatar')
                user.avatar.delete(save=False)
            if user:
                serializer = UserRegisterSerializer(user, data=data)
                serializer.is_valid(raise_exception=True)
                user:User = serializer.save()
            if hasattr(user, "guest_profile"):
                guest:Guest = user.guest_profile
                guest_serializer = self.get_serializer(instance=guest, data=data)
                guest_serializer.is_valid(raise_exception=True)
                guest_serializer.save()
            return Response(guest_serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(e)
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class EmployeeRegisterView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = EmployeeSerializer
    queryset = User.objects.none()
    http_method_names =["put","post"]
    lookup_field="id"

    @transaction.atomic
    def create(self, request):
        data = request.data
        data["user_type"]=User.UserTypes.EMPLOYEE

        serializer = UserRegisterSerializer(data=data)
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
    
    @transaction.atomic
    def update(self, request, *args, **kwargs):
        try:
            data = request.data
            if not "id" in data:
                return Response("ID is required", status=status.HTTP_400_BAD_REQUEST)
            id = data.get("id")
            user = User.objects.get(id=id)
            if request.FILES.get('avatar'):
                data['avatar'] = request.FILES.get('avatar')
                user.avatar.delete(save=False)
          
            if user:
                serializer = UserRegisterSerializer(user, data=data)
                serializer.is_valid(raise_exception=True)
                user:User = serializer.save()
            if hasattr(user, "employee_profile"):
                employee:Employee = user.employee_profile
                employee_serializer = self.get_serializer(instance=employee, data=data)
                employee_serializer.is_valid(raise_exception=True)
                employee_serializer.save()
            return Response(
                employee_serializer.data,
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            print(e)
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
    authentication_classes = []

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        refresh = data.pop("refresh")
        user = data.pop("user")
        access = data.pop("access")
        response = Response(user, status=status.HTTP_200_OK)
        logger.info('User Logged In.', extra={
            'user_id': user.get("id"),
            'first_name':user.get("first_name"),
        })
        # logger.info('Log message with structured logging.', extra={
        #     'item': "Orange Soda",
        #     'price': 100.00
        # })
        response.set_cookie(
            "access",
            access,
            httponly=True,
            secure=False,
            samesite="Lax",
            path="/",
            max_age=60 * 60 * 24 * 30,
        )

        response.set_cookie(
            "refresh",
            refresh,
            httponly=True,
            secure=False,
            samesite="Lax",
            path="/",
            max_age=60 * 60 * 24 * 30,
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
        try:
            user:User = request.user
            data = request.data
            if request.FILES.get('avatar'):
                data['avatar'] = request.FILES.get('avatar')
                user.avatar.delete(save=False)
            user_serializer = UserSerializer(user, data=data, partial=True)
            user_serializer.is_valid(raise_exception=True)
            user_serializer.save()
            if hasattr(user, "employee_profile"):
                employee = user.employee_profile
                emp_serializer = EmployeeSerializer(employee, data=data, partial=True)
                emp_serializer.is_valid(raise_exception=True)
                emp_serializer.save()
            if hasattr(user, "guest_profile"):
                guest = user.guest_profile
                cus_serializer = GuestSerializer(guest, data=data, partial=True)
                cus_serializer.is_valid(raise_exception=True)
                cus_serializer.save()

            serializer = UnifiedUserSerializer(user)
            return Response(serializer.data)
        except Exception as e:
            print(e)
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
