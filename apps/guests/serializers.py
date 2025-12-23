from rest_framework import serializers

from apps.guests.models import Guest



class GuestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guest
        exclude=["restored_at", "deleted_at", "transaction_id","id"
                 ]
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["guest_id"] = instance.id
        return representation
