from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import ListAPIView, get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.cache import cache
from apps.models import Warehouse, User
from apps.serializers.branch import BulkTransferSerializer
from apps.serializers.warehouse import WarehouseSerializer
from house.models import Product, ProductTransfer


class BranchListApiView(ListAPIView):
    serializer_class = WarehouseSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Warehouse.objects.filter(user=user).order_by('id').all()
        else:
            return Warehouse.objects.none()


@extend_schema(
    tags=['Transfer'],
)
@extend_schema(
    tags=["Transfer"],
    request=BulkTransferSerializer,
    responses={201: {"message": "All products transferred successfully."}},
)
class BulkTransferAPIView(APIView):
    def post(self, request):
        user = request.user

        if user.role != User.RoleStatus.SUPERUSER:
            return Response(status=status.HTTP_403_FORBIDDEN)

        from_warehouse_id = cache.get(f"user_{user.id}_warehouse_id")
        if not from_warehouse_id:
            return Response({"error": "From warehouse not found in cache."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = BulkTransferSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        to_warehouse_id = serializer.validated_data["to_warehouse"]
        items = serializer.validated_data["items"]

        from_warehouse = get_object_or_404(Warehouse, id=from_warehouse_id)
        to_warehouse = get_object_or_404(Warehouse, id=to_warehouse_id)

        for item in items:
            product = get_object_or_404(Product, id=item["product_id"])
            ProductTransfer.objects.create(
                from_warehouse=from_warehouse,
                to_warehouse=to_warehouse,
                product=product,
                quantity=item["quantity"]
            )

        return Response({"message": "All products transferred successfully."}, status=status.HTTP_201_CREATED)
