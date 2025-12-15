from rest_framework.routers import DefaultRouter
from .views import RoomViewSet,RoomTypeViewSet

router = DefaultRouter()
router.register(r'type', RoomTypeViewSet, basename='room-type')
router.register(r'', RoomViewSet, basename='room')

urlpatterns = router.urls
