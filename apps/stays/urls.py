from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register("reservations", ReservationViewSet)
router.register("stays", StayViewSet)
router.register("folios", FolioViewSet)
router.register("charges", ChargeViewSet)
router.register("payments", PaymentViewSet)
router.register("adjustments", FolioAdjustmentViewSet)
router.register("menu-items", MenuItemViewSet)
router.register("food-orders", FoodOrderViewSet)
router.register("food-order-items", FoodOrderItemViewSet)

urlpatterns = router.urls
