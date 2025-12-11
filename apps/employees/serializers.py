from rest_framework import serializers

from apps.employees.models import Employee



class EmployeeSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        exclude = ["deleted_at", "restored_at", "transaction_id"]

    def get_user(self, obj:Employee):
        from apps.users.serializers import UserSerializer
        return UserSerializer(obj.user, context=self.context).data

