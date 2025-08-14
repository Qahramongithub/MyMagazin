from django.core.cache import cache
from django.db.models import Sum, Case, When, F, ExpressionWrapper, FloatField
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.models import User
from house.models import Product, OrderItem
from house.serializers.analitica import ExelSerializer, AnaliticaSerializer
from house.serializers.order import OrderItemSerializer


@extend_schema(
    tags=['analitica'],
)
class DailySaleListView(ListAPIView):
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        today = timezone.now().date()
        warehouse = cache.get(f"user_{user.id}_warehouse_id")

        return OrderItem.objects.filter(
            order__created_at__date=today,
            order__warehouse_id=warehouse
        )


@extend_schema(
    tags=['analitica'],
)
class MonthlySaleListView(ListAPIView):
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        warehouse_id = cache.get(f"user_{user.id}_warehouse_id")

        if not warehouse_id:
            return OrderItem.objects.none()

        now = timezone.now()

        return OrderItem.objects.filter(
            order__created_at__month=now.month,
            order__created_at__year=now.year,
            order__warehouse_id=warehouse_id
        )


# @extend_schema(
#     tags=['analitica'],
#     request=ExelSerializer,
# )
# class SaleListView(APIView):
#     permission_classes = [IsAuthenticated]
#
#     def post(self, request, *args, **kwargs):
#         user = request.user
#
#         if not user.is_authenticated:
#             return Response({"detail": "Foydalanuvchi tizimga kirmagan"}, status=401)
#
#         serializer = ExelSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         start_date = serializer.validated_data['start_date']
#         end_date = serializer.validated_data['end_date']
#
#         warehouse_id = cache.get(f"user_{user.id}_warehouse_id")
#         if not warehouse_id:
#             return Response({"detail": "Ombor aniqlanmadi"}, status=400)
#
#         products = OrderItem.objects.filter(
#             created_at__gt=start_date,
#             created_at__lt=end_date,
#             warehouse_id=warehouse_id
#         )
#
#         data = OrderItemSerializer(products, many=True).data
#         return Response(data)

@extend_schema(
    tags=["analitica"], responses=AnaliticaSerializer)
class AnaliticaListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        if user.role != User.RoleStatus.SUPERUSER:
            return Response({'message': 'You are not the superuser'}, status=status.HTTP_403_FORBIDDEN)
        warehouse_id = cache.get(f"user_{user.id}_warehouse_id")
        products = Product.objects.filter(warehouse_id=warehouse_id)
        total_price = products.aggregate(
            total=Sum(
                ExpressionWrapper(
                    Case(
                        When(discount_price__gt=0, then=F('discount_price')),
                        default=F('price')
                    ) * F('quantity'),
                    output_field=FloatField()
                )
            )
        )['total'] or 0
        base_price = products.aggregate(
            total=Sum(
                ExpressionWrapper(
                    F('base_price') * F('quantity'),
                    output_field=FloatField()  # ← bu joy majburiy
                )
            )
        )['total'] or 0
        profit_price = base_price - total_price

        return Response({
            "total_price": total_price,
            "base_price": base_price,
            "profit_price": profit_price,
        })
