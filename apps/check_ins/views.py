from rest_framework import viewsets
from .models import CheckIn
from .serializers import CheckInSerializer
from rest_framework.response import Response
from rest_framework import status
from django_filters.rest_framework import DjangoFilterBackend

class CheckInViewSet(viewsets.ModelViewSet):
    queryset = CheckIn.objects.all()
    serializer_class = CheckInSerializer
    filter_backends = [DjangoFilterBackend]

    def create(self, request, *args, **kwargs):
        data = request.data
        self.get_serializer_class(data)
        self.serializer_class.is_valid()
        return Response("Created", status=status.HTTP_201_CREATED)
        # return super().create(request, *args, **kwargs)
