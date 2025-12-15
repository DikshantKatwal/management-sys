from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from decimal import Decimal

from .models import (
    Reservation, Stay, StayExtension,
    Folio, Charge, Payment, FolioAdjustment,
    MenuItem, FoodOrder, FoodOrderItem
)
from .serializers import *


# ---------- Reservation ----------

class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.select_related("guest", "room", "room_type")
    serializer_class = ReservationSerializer


# ---------- Stay ----------

class StayViewSet(viewsets.ModelViewSet):
    queryset = Stay.objects.select_related("reservation", "room")
    serializer_class = StaySerializer

    @action(detail=True, methods=["post"])
    def extend(self, request, pk=None):
        stay = self.get_object()
        new_date = request.data.get("new_check_out_date")
        reason = request.data.get("reason", "")

        if not new_date:
            return Response(
                {"detail": "new_check_out_date is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            StayExtension.objects.create(
                stay=stay,
                old_check_out_date=stay.expected_check_out_date,
                new_check_out_date=new_date,
                reason=reason,
            )
            stay.expected_check_out_date = new_date
            stay.save(update_fields=["expected_check_out_date"])

        return Response({"status": "extended"})


# ---------- Folio ----------

class FolioViewSet(viewsets.ModelViewSet):
    queryset = Folio.objects.select_related("stay")
    serializer_class = FolioSerializer

    @action(detail=True, methods=["post"])
    def close(self, request, pk=None):
        folio = self.get_object()
        if folio.is_closed:
            return Response({"detail": "Folio already closed"})
        folio.is_closed = True
        folio.save(update_fields=["is_closed"])
        return Response({"status": "folio closed"})


class ChargeViewSet(viewsets.ModelViewSet):
    queryset = Charge.objects.select_related("folio", "created_by")
    serializer_class = ChargeSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.select_related("folio", "created_by")
    serializer_class = PaymentSerializer


class FolioAdjustmentViewSet(viewsets.ModelViewSet):
    queryset = FolioAdjustment.objects.select_related("folio", "created_by")
    serializer_class = FolioAdjustmentSerializer


# ---------- Menu & Food ----------

class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.filter(is_active=True)
    serializer_class = MenuItemSerializer


class FoodOrderViewSet(viewsets.ModelViewSet):
    queryset = FoodOrder.objects.select_related("stay")
    serializer_class = FoodOrderSerializer

    @action(detail=True, methods=["post"])
    def post_to_folio(self, request, pk=None):
        order = self.get_object()
        folio = order.stay.folio

        if folio.is_closed:
            return Response(
                {"detail": "Folio is closed"},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            for item in order.items.all():
                Charge.objects.create(
                    folio=folio,
                    category=Charge.Category.FOOD,
                    description=item.menu_item.name,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                )
            order.status = FoodOrder.Status.DELIVERED
            order.save(update_fields=["status"])

        return Response({"status": "posted to folio"})


class FoodOrderItemViewSet(viewsets.ModelViewSet):
    queryset = FoodOrderItem.objects.select_related("order", "menu_item")
    serializer_class = FoodOrderItemSerializer
