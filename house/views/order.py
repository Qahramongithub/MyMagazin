from datetime import date

from django.core.cache import cache
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveAPIView, GenericAPIView
from rest_framework.permissions import IsAuthenticated
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

@extend_schema(
    parameters=[
        OpenApiParameter(
            name='start_date',
            type=OpenApiTypes.DATE,
            description='Boshlanish sanasi (YYYY-MM-DD)',
            required=True,
        ),
        OpenApiParameter(
            name='end_date',
            type=OpenApiTypes.DATE,
            description='Tugash sanasi (YYYY-MM-DD)',
            required=True,
        ),
    ],
    responses=OrderSerializer
)
@extend_schema(
    tags=['Order'],
)
class OrderExel(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get(self, request):
        user = request.user
        warehouse_id = cache.get(f"user_{user.id}_warehouse_id")

        if not warehouse_id:
            return Response(
                {"detail": "Warehouse aniqlanmadi."},
                status=status.HTTP_400_BAD_REQUEST
            )

        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if not start_date or not end_date:
            return Response(
                {"detail": "start_date va end_date majburiy"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            start_date = date.fromisoformat(start_date)
            end_date = date.fromisoformat(end_date)

        except ValueError:
            return Response(
                {"detail": "Sana formati YYYY-MM-DD bo‘lishi kerak"},
                status=status.HTTP_400_BAD_REQUEST
            )

        queryset = Order.objects.filter(
            warehouse_id=warehouse_id,
            created_at__date__range=(start_date, end_date)
        )

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

