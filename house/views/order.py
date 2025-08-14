from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from django.core.cache import cache
from rest_framework.response import Response

from house.models import Order
from house.serializers.order import OrderSerializer


@extend_schema(
    tags=['Order'],
)
class OrderListCreateAPIView(ListCreateAPIView):
    queryset = Order.objects.all().order_by('-created_at')
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]


class OrderDeleteApiView(RetrieveAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'
    lookup_url_kwarg = 'id'

    def delete(self, request, *args, **kwargs):
        user = request.user
        warehouse_id = cache.get(f"user_{user.id}_warehouse_id")

        if not warehouse_id:
            return Response(
                {"detail": "Warehouse aniqlanmadi."},
                status=status.HTTP_400_BAD_REQUEST
            )

        order = self.get_object()

        if order.warehouse_id != warehouse_id:
            return Response(
                {"detail": "Bu Order sizning Warehouse ichida emas."},
                status=status.HTTP_403_FORBIDDEN
            )

        for item in order.orderitem_set.all():
            product = item.product
            if product:
                product.quantity += item.quantity
                product.save(update_fields=['quantity'])

        order.delete()

        return Response(
            {"detail": "Order o‘chirildi va maxsulot  qaytarildi."},
            status=status.HTTP_204_NO_CONTENT
        )
