from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from apps.utilities.models import Country, Zone
from apps.utilities.serializers import CountrySerializer, ZoneSerializer
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

class CountryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Country objects with read-only access.
    This ViewSet provides a read-only API endpoint for retrieving country data.
    It includes caching for performance optimization and supports filtering and
    searching capabilities.
    Attributes:
        http_method_names (list): Allowed HTTP methods. Only GET requests are permitted.
        queryset (QuerySet): All Country objects from the database.
        authentication_classes (list): No authentication required for access.
        permission_classes (list): No permission restrictions applied.
        serializer_class (Serializer): CountrySerializer for serializing Country objects.
        filter_backends (list): Enables filtering via DjangoFilterBackend and searching via SearchFilter.
        filterset_fields (dict): Defines filterable fields:
            - id: Exact match filtering
            - country_name: Case-insensitive substring matching
            - iso3: Case-insensitive substring matching
        search_fields (list): Fields available for full-text search (country_name, iso3).
    Methods:
        list: Returns a cached list of countries. Results are cached for 24 hours (86400 seconds)
              to improve performance on repeated requests.
    Note:
        This ViewSet is read-only and does not support create, update, or delete operations.
    """
    http_method_names =["get"]
    queryset = Country.objects.all()
    authentication_classes = []
    permission_classes = []
    serializer_class = CountrySerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]

    filterset_fields = {
        "id": ["exact"],
        "country_name": ["icontains"],
        "iso3": ["icontains"],
    }

    search_fields = ["country_name", "iso3"]

    @method_decorator(cache_page(60 * 60 * 24))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

class ZoneViewSet(viewsets.ModelViewSet):
    """
    ZoneViewSet
    A read-only ViewSet for managing Zone objects with filtering and caching capabilities.
    This ViewSet provides a list endpoint for retrieving zones with related country information.
    The list endpoint is cached for 24 hours to improve performance.
    Attributes:
        http_method_names (list): Allowed HTTP methods. Only GET requests are permitted.
        queryset (QuerySet): Base queryset that retrieves Zone objects with select_related
            optimization for the related 'country' field.
        authentication_classes (list): Authentication classes. Empty list means no authentication
            is required.
        permission_classes (list): Permission classes. Empty list means no permission checks
            are enforced.
        serializer_class (Serializer): ZoneSerializer used for serializing/deserializing data.
        filter_backends (list): Applied filter backends including DjangoFilterBackend for
            filtering and SearchFilter for searching.
        filterset_fields (dict): Filter field configuration allowing exact filtering on 'id'
            and 'country' fields.
        search_fields (list): Fields available for search queries including 'name' and
            'country__country_name'.
    Methods:
        list(request, *args, **kwargs): Retrieves a list of zones with 24-hour caching.
    """
    http_method_names = ["get"]
    queryset = Zone.objects.select_related("country")
    authentication_classes = []
    permission_classes = []
    serializer_class = ZoneSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter]

    filterset_fields = {
        "id": ["exact"],
        "country": ["exact"],
    }
    search_fields = [
        "name",
        "country__country_name"
    ]

    @method_decorator(cache_page(60 * 60 * 24))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)