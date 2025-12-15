from rest_framework import viewsets

from apps.users.models import User
from apps.users.serializers import UnifiedUserSerializer, UserSerializer
from .models import Employee
from .serializers import EmployeeSerializer
from django.db import transaction
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(employee_profile__isnull=False)
    serializer_class = UnifiedUserSerializer


    
class UserAPIView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UnifiedUserSerializer

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

        # Update employee/guest profile
        if hasattr(user, "employee_profile"):
            employee = user.employee_profile
            emp_serializer = EmployeeSerializer(employee, data=data, partial=True)
            emp_serializer.is_valid(raise_exception=True)
            emp_serializer.save()

        serializer = UnifiedUserSerializer(user)
        return Response(serializer.data)