from rest_framework.routers import DefaultRouter

from apps.guests.views import GuestViewSet

router = DefaultRouter()
router.register(r'', GuestViewSet)

urlpatterns = router.urls
