from rest_framework import serializers

from apps.employees.models import Employee



class EmployeeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Employee
        exclude = ["id","deleted_at", "restored_at", "transaction_id","user"]

   
