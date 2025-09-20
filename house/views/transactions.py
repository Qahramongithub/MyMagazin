from django.core.exceptions import ValidationError
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import CreateAPIView, UpdateAPIView, ListAPIView
from django.core.cache import cache
from rest_framework.response import Response
from rest_framework.views import APIView

from house.models import Transactions
from house.serializers.transaction import TransactionModelSerializer


@extend_schema(
    tags=['Transactions'],
    responses={
        status.HTTP_200_OK: TransactionModelSerializer,
    }
)
class TransactionCreateApiView(CreateAPIView):
    queryset = Transactions.objects.all()
    serializer_class = TransactionModelSerializer

    def perform_create(self, serializer):
        user = self.request.user
        warehouse_id = cache.get(f"user_{user.id}_warehouse_id")
        if not warehouse_id:
            raise ValidationError({"warehouse": "Warehouse id not found in cache"})
        serializer.save(warehouse_id=warehouse_id)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@extend_schema(
    tags=['Transactions'],
    responses={
        status.HTTP_200_OK: TransactionModelSerializer,
    }
)
class TransactionListApiView(ListAPIView):
    queryset = Transactions.objects.all()
    serializer_class = TransactionModelSerializer

    def get_queryset(self):
        user = self.request.user
        warehouse_id = cache.get(f"user_{user.id}_warehouse_id")
        if warehouse_id is None:
            raise ValidationError({"warehouse": "Warehouse id not found in cache"})
        return Transactions.objects.filter(warehouse_id=warehouse_id).order_by("-created_at")


@extend_schema(
    tags=['Transactions'],
    responses={
        status.HTTP_200_OK: TransactionModelSerializer,
    }
)
class TransactionUpdateApiView(UpdateAPIView):
    queryset = Transactions.objects.all()
    serializer_class = TransactionModelSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        user = request.user
        warehouse_id = cache.get(f"user_{user.id}_warehouse_id")
        if not warehouse_id:
            raise ValidationError({"warehouse": "Warehouse id not found in cache"})

        serializer.save(warehouse_id=warehouse_id)
        return Response(serializer.data, status=status.HTTP_200_OK)



