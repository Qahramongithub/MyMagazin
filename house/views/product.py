from django.core.cache import cache
from django.db.models import F
from drf_spectacular.utils import extend_schema
from rest_framework.exceptions import ValidationError
from rest_framework.generics import CreateAPIView, UpdateAPIView, DestroyAPIView, ListAPIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated

from apps.models import Warehouse
from house.models import Product
from house.serializers.product import ProductModelSerializer


@extend_schema(
    tags=['Products'],
    responses=ProductModelSerializer,
    request=ProductModelSerializer,
)
class ProductCreateApiView(CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductModelSerializer
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        user = self.request.user
        warehouse_id = cache.get(f"user_{user.id}_warehouse_id")
        if not warehouse_id:
            raise ValidationError({"warehouse": "Warehouse id not found in cache"})

        try:
            warehouse = Warehouse.objects.get(id=warehouse_id)
        except Warehouse.DoesNotExist:
            raise ValidationError({"warehouse": "Invalid warehouse id"})

        sku = serializer.validated_data.get("sku")

        if Product.objects.filter(sku=sku, warehouse=warehouse).exists():
            raise ValidationError({"detail": f"Mahsulot (sku={sku}) ushbu omborda allaqachon mavjud"})

        serializer.save(warehouse=warehouse)


@extend_schema(
    tags=['Products'],
)
class ProductUpdateApiView(UpdateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductModelSerializer
    lookup_field = 'pk'

    def perform_update(self, serializer):
        user = self.request.user
        warehouse_id = cache.get(f"user_{user.id}_warehouse_id")
        if warehouse_id:
            try:
                warehouse = Warehouse.objects.get(id=warehouse_id)
                serializer.save(warehouse=warehouse)
            except Warehouse.DoesNotExist:
                raise ValidationError({"warehouse": "Invalid warehouse id"})
        else:
            raise ValidationError({"warehouse": "Warehouse id not found in cache"})


@extend_schema(
    tags=['Products'],
)
class ProductDeleteApiView(DestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductModelSerializer
    lookup_field = 'pk'


@extend_schema(tags=['Products'])
class ProductListApiView(ListAPIView):
    serializer_class = ProductModelSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        warehouse_id = cache.get(f"user_{user.id}_warehouse_id")
        if warehouse_id is None:
            return Product.objects.none()
        return Product.objects.filter(warehouse_id=warehouse_id, quantity__gt=0).order_by('-id')


@extend_schema(
    tags=['Products'],
)
class FinishedProductListApiView(ListAPIView):
    serializer_class = ProductModelSerializer

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Product.objects.none()
        warehouse_id = cache.get(f"user_{user.id}_warehouse_id")
        return Product.objects.filter(warehouse_id=warehouse_id, quantity=0)


@extend_schema(
    tags=['Products'],
)
class LowProductListApiView(ListAPIView):
    serializer_class = ProductModelSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Product.objects.none()

        warehouse_id = cache.get(f"user_{user.id}_warehouse_id")
        if warehouse_id is None:
            return Product.objects.none()

        return Product.objects.filter(
            warehouse_id=warehouse_id,
            quantity__lt=F('min_quantity'),
            quantity__gt=0,
        )
