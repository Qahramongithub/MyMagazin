from django.core.cache import cache  # Redis uchun
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView, UpdateAPIView, DestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.models import Warehouse, User
from apps.serializers.warehouse import WarehouseSerializer


@extend_schema(
    tags=['Warehouse'],
)
class WarehouseCreateApiView(CreateAPIView):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer
    permission_classes = [IsAuthenticated]


@extend_schema(
    tags=['Warehouse'],
)
class WarehouseListApiView(ListAPIView):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.role == User.RoleStatus.SUPERUSER:
            return Warehouse.objects.filter(user=user.id)

        return Warehouse.objects.filter(user=user.id)


@extend_schema(
    tags=['Warehouse'],
)
class WarehouseDetailApiView(RetrieveAPIView):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'
    lookup_url_kwarg = 'pk'


@extend_schema(
    tags=['Warehouse'],
)
class WarehouseUpdateApiView(UpdateAPIView):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'
    lookup_url_kwarg = 'pk'


@extend_schema(
    tags=['Warehouse'],
)
class WarehouseDeleteApiView(DestroyAPIView):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'
    lookup_url_kwarg = 'pk'

    def delete(self, request, *args, **kwargs):
        user = request.user
        if user.role != User.RoleStatus.SUPERUSER:
            return Response(status=status.HTTP_403_FORBIDDEN)
        return Warehouse.objects.filter(id=kwargs['pk']).delete()


class WarehouseUserApiView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.is_authenticated:
            warehouses = Warehouse.objects.filter(user=user.id).all()
            serializer = WarehouseSerializer(warehouses, many=True)
            return Response(serializer.data)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)


@extend_schema(
    tags=['Warehouse'],
    responses=WarehouseSerializer  # 🟢 Swagger uchun
)
class WarehouseStartApiView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = WarehouseSerializer

    def get(self, request):
        user = request.user

        warehouse_id = cache.get(f"user_{user.id}_warehouse_id")
        if warehouse_id:
            warehouse = Warehouse.objects.filter(id=warehouse_id).first()
        else:
            warehouse = Warehouse.objects.filter(user=user).order_by('id').first()
            if warehouse:
                cache.set(f"user_{user.id}_warehouse_id", warehouse.id, timeout=None)

        if not warehouse:
            return Response({'detail': "Ombor ma'lumotlari topilmadi."}, status=status.HTTP_404_NOT_FOUND)

        # ✅ Ma'lumot bor
        return Response(WarehouseSerializer(warehouse).data)


@extend_schema(
    tags=['Warehouse'],
    responses=WarehouseSerializer  # 🟢 natijada bu qaytadi
)
class WarehouseEndApiView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = WarehouseSerializer  # 🟢 schema uchun

    def post(self, request, pk):
        user = request.user
        if not user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        warehouse = Warehouse.objects.filter(id=pk, user=user).first()
        if not warehouse:
            return Response({"detail": "Sklad topilmadi"}, status=404)

        cache.set(f"user_{user.id}_warehouse_id", warehouse.id, timeout=None)
        return Response({
            "detail": "Sklad muvaffaqiyatli tanlandi",
            "warehouse": WarehouseSerializer(warehouse).data
        }, status=status.HTTP_200_OK)
