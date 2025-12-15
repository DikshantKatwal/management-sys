from rest_framework import serializers
from apps.rooms.models import Room,RoomType



class RoomTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomType
        fields = ["id", "name", "max_occupancy","base_rate","description"]
    

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ["id", "room_type","number","floor","status","sequence"]
    

    # def to_representation(self, instance:Room):
    #     rep_data = super().to_representation(instance)
    #     if instance.room_type:
    #         rep_data["room_type"] = {
    #             "id":instance.room_type_id,
    #             "label":instance.room_type.name
    #         }
    #     return rep_data