from rest_framework.routers import DefaultRouter
from apps.utilities.views import CountryViewSet, ZoneViewSet

router = DefaultRouter()
router.register(r'country', CountryViewSet, basename='country')
router.register(r'zone', ZoneViewSet, basename='zone')

urlpatterns = router.urls
