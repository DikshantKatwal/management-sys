from rest_framework import serializers
from apps.rooms.models import Room


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ["id", "name","type","sequence","status"]
    
    def update(self, instance, validated_data):
        print(validated_data)
        return super().update(instance, validated_data)
