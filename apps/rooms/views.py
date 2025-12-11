from rest_framework import viewsets, generics
from .models import Room
from .serializers import RoomSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter


class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all().order_by("sequence")
    serializer_class = RoomSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['name','type',"status"]
