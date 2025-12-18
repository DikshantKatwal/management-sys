from rest_framework import viewsets

from apps.users.models import User
from apps.users.serializers import UnifiedUserSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter


class GuestViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(guest_profile__isnull=False)
    serializer_class = UnifiedUserSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['first_name','last_name',
                     'email',"phone",
                     "guest_profile__address",
                     "guest_profile__identification",
                     "guest_profile__id_number",
                     ]
