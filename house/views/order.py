from django.core.cache import cache
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.generics import ListCreateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from house.models import Order
from house.serializers.order import OrderSerializer,OrderExcelRequestSerializer


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
    tags=['Order'],
    request=OrderExcelRequestSerializer,
    responses=OrderSerializer(many=True),
)
class OrderExel(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def post(self, request):
        user = request.user
        warehouse_id = cache.get(f"user_{user.id}_warehouse_id")

        if not warehouse_id:
            return Response(
                {"detail": "Warehouse aniqlanmadi."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # request body dan olish
        req_serializer = OrderExcelRequestSerializer(data=request.data)
        req_serializer.is_valid(raise_exception=True)

        start_date = req_serializer.validated_data['start_date']
        end_date = req_serializer.validated_data['end_date']

        queryset = Order.objects.filter(
            warehouse_id=warehouse_id,
            created_at__date__range=(start_date, end_date)
        )

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
