from calendar import month_name

from django.core.cache import cache
from django.db.models import Sum, Case, When, F, ExpressionWrapper, FloatField, Count
from django.db.models.functions import ExtractYear, ExtractMonth
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.models import User
from house.models import Product, OrderItem, Transactions, Order
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


@extend_schema(
    tags=['analitica'],
    request=ExelSerializer,
    responses={200: OrderItemSerializer(many=True)}  # chiroyliroq
)
class SaleListView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user

        if not user.is_authenticated:
            return Response({"detail": "Foydalanuvchi tizimga kirmagan"}, status=401)

        serializer = ExelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        start_date = serializer.validated_data['start_date']
        end_date = serializer.validated_data['end_date']

        warehouse_id = cache.get(f"user_{user.id}_warehouse_id")
        if not warehouse_id:
            return Response({"detail": "Ombor aniqlanmadi"}, status=400)

        products = OrderItem.objects.filter(
            created_at__gte=start_date,
            created_at__lte=end_date,
            warehouse_id=warehouse_id
        )

        return Response(OrderItemSerializer(products, many=True).data)


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
        transaction = Transactions.objects.filter(warehouse_id=warehouse_id)
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
        transaction_price = transaction.aggregate(
            total=Sum(
                Case(
                    When(status='intro', then=F('price')),  # kirim bo‘lsa qo‘shiladi
                    When(status='exit', then=-F('price')),  # chiqim bo‘lsa ayiriladi
                    output_field=FloatField()
                )
            )
        )['total'] or 0
        profit_price = total_price - base_price + transaction_price

        return Response({
            "total_price": total_price,
            "base_price": base_price,
            "profit_price": profit_price,
        })


@extend_schema(
    tags=["analitica"], )
class ReportListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        if user.role != User.RoleStatus.SUPERUSER:
            return Response({'message': 'You are not the superuser'}, status=403)

        warehouse_id = cache.get(f"user_{user.id}_warehouse_id")

        order_items = (
            OrderItem.objects
            .filter(order__warehouse_id=warehouse_id)
            .annotate(
                year=ExtractYear('order__created_at'),
                month=ExtractMonth('order__created_at'),
                final_price=ExpressionWrapper(
                    Case(
                        When(product__discount_price__gt=0, then=F('product__discount_price')),
                        default=F('product__price')
                    ) * F('quantity'),
                    output_field=FloatField()
                ),
                base_calc=ExpressionWrapper(
                    F('product__base_price') * F('quantity'),
                    output_field=FloatField()
                )
            )
            .values('year', 'month')
            .annotate(
                total_price=Sum('final_price'),
                base_price=Sum('base_calc'),
            )
            .order_by('year', 'month')
        )

        final_data = []
        for item in order_items:
            total_price = item.get('total_price') or 0
            base_price = item.get('base_price') or 0
            profit = base_price - total_price  # foyda

            final_data.append({
                "year": item.get('year'),
                "month": item.get('month'),
                "total_price": total_price,
                "base_price": base_price,
                "profit_price": profit
            })

        return Response(final_data)
