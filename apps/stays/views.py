from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django.db.models import F, Sum
from decimal import Decimal
from rest_framework.exceptions import PermissionDenied
from django.utils import timezone
from rest_framework.exceptions import ValidationError
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
    def checkout(self, request, pk=None):
        stay = self.get_object()

        if stay.status != Stay.Status.IN_HOUSE:
            raise ValidationError("Stay is not in-house")

        folio = stay.folio

        # Calculate balance
        charges_total = folio.charges.aggregate(
            total=Sum(
                (F("quantity") * F("unit_price"))
                + F("tax_amount")
                - F("discount_amount")
            )
        )["total"] or 0

        payments_total = folio.payments.aggregate(
            total=Sum("amount")
        )["total"] or 0

        adjustments_total = folio.adjustments.aggregate(
            total=Sum("amount")
        )["total"] or 0

        balance = charges_total + adjustments_total - payments_total

        if balance != 0:
            raise ValidationError(
                f"Outstanding balance: {balance}"
            )

        with transaction.atomic():
            # Update stay
            stay.status = Stay.Status.CHECKED_OUT
            stay.checked_out_at = timezone.now()
            stay.save(update_fields=["status", "checked_out_at"])

            # Update reservation
            reservation = stay.reservation
            reservation.status = Reservation.Status.CHECKED_OUT
            reservation.save(update_fields=["status"])

            # Close folio
            folio.is_closed = True
            folio.save(update_fields=["is_closed"])

        return Response({"status": "checked out successfully"})
    

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
            return Response(
                {"detail": "Folio already closed"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not folio.is_balanced():
            return Response(
                {
                    "detail": "Folio cannot be closed because balance is not zero",
                    "balance": folio.balance
                },
                status=status.HTTP_400_BAD_REQUEST
            )

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
    queryset = FoodOrder.objects.select_related("stay").prefetch_related("items")
    serializer_class = FoodOrderSerializer

    def get_serializer_class(self):
        if self.action == "create":
            return FoodOrderCreateSerializer
        return FoodOrderSerializer
    
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

    def perform_create(self, serializer):
        raise PermissionDenied("Items must be created via FoodOrder")

    def perform_update(self, serializer):
        raise PermissionDenied("Items cannot be updated directly")