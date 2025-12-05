from rest_framework.routers import DefaultRouter

from apps.check_ins.views import CheckInViewSet

router = DefaultRouter()
router.register(r'', CheckInViewSet)

urlpatterns = router.urls
