from rest_framework.routers import DefaultRouter

from apps.employees.views import EmployeeViewSet

router = DefaultRouter()
router.register(r'', EmployeeViewSet)

urlpatterns = router.urls
