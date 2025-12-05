from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from apps.common.permissions import IsAdminUser
from .serializers import (
    CustomerRegisterSerializer,
    EmployeeRegisterSerializer,
    LoginSerializer,
)
from rest_framework_simplejwt.tokens import RefreshToken



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


class EmployeeRegisterView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        serializer = EmployeeRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {"message": "Employee created successfully", "id": str(user.id)},
            status=status.HTTP_201_CREATED
        )



class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        refresh = data.pop("refresh")
        user = data.pop("user")
        access = data.pop("access")
        response = Response(user, status=status.HTTP_200_OK)
        response.set_cookie(
            httponly=True,
            key='refresh',
            value=refresh,
            secure=True
        )
        response.set_cookie(
            httponly=True,
            key='access',
            value=access,
            secure=True
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
        
class UserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        return Response({
            "id": str(user.id),
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "user_type": user.user_type,
        })