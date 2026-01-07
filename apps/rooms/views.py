from rest_framework import viewsets, generics
from .models import Room,RoomType
from .serializers import RoomSerializer, RoomTypeSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter


class RoomTypeViewSet(viewsets.ModelViewSet):
    queryset = RoomType.objects.all()
    serializer_class = RoomTypeSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['name','max_occupancy',"base_rate","description"]


class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all().order_by("sequence")
    serializer_class = RoomSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['number','room_type__name',"status"]

    filterset_fields = {
        "room_type": ["exact"],
    }
