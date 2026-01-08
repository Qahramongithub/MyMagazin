import io

from django.core.cache import cache
from django.http import HttpResponse
from drf_spectacular.utils import extend_schema
from openpyxl import Workbook
from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from house.models import Order
from house.serializers.order import OrderSerializer, OrderExcelRequestSerializer


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


class OrderExcel(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        warehouse_id = cache.get(f"user_{user.id}_warehouse_id")

        if not warehouse_id:
            return Response(
                {"detail": "Warehouse aniqlanmadi."},
                status=status.HTTP_400_BAD_REQUEST
            )

        req_serializer = OrderExcelRequestSerializer(data=request.data)
        req_serializer.is_valid(raise_exception=True)

        start_date = req_serializer.validated_data['start_date']
        end_date = req_serializer.validated_data['end_date']

        orders = Order.objects.filter(
            warehouse_id=warehouse_id,
            created_at__date__range=(start_date, end_date)
        ).prefetch_related('orderitem_set__product')

        wb = Workbook()
        ws = wb.active
        ws.title = "Buyurtmalar"

        # Sana va vaqtni alohida ustunga ajratamiz
        ws.append([
            "Mahsulot nomi",
            "Miqdori",
            "Narxi",
            "O‘lchov birligi",
            "Jami summa",
            "Sana",  # 2026-01-08
            "Vaqt" # 21:54:33
        ])

        for order in orders:
            # created_at dan sana va vaqtni ajratamiz
            order_date = order.created_at.date()  # Faqat sana
            order_time = order.created_at.time()  # Faqat vaqt

            for item in order.orderitem_set.all():
                ws.append([
                    item.product.name,
                    float(item.quantity),
                    float(item.price),
                    item.product.unit,
                    float(item.quantity) * float(item.price),
                    order_date,  # Sana
                    order_time,  # Vaqt
                ])

        # BytesIO yordamida xotiraga saqlaymiz
        excel_file = io.BytesIO()
        wb.save(excel_file)
        excel_file.seek(0)  # Fayl boshiga qaytamiz

        response = HttpResponse(
            excel_file.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="buyurtmalar.xlsx"'

        excel_file.close()  # Resursni tozalaymiz

        return response