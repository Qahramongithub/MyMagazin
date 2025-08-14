from django.core.cache import cache
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import CreateAPIView, DestroyAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.models import User
from house.models import Category
from house.serializers.category import CategorySerializer


@extend_schema(tags=['category'])
class CategoryCreateApiView(CreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user

        if user.role != User.RoleStatus.SUPERUSER:
            raise PermissionDenied("Sizda ruxsat yo'q")  # <-- mana bu to'g'ri

        serializer.save()


@extend_schema(
    tags=['category'],
    responses=CategorySerializer(many=True)  # drf-spectacular uchun
)
class CategoryListApiView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CategorySerializer  # ✅ schema uchun kerak

    def get(self, request):
        user = request.user
        warehouse_id = cache.get(f"user_{user.id}_warehouse_id")

        if not user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        categories = Category.objects.filter(warehouse_id=warehouse_id)
        serializer = self.serializer_class(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    tags=['category'],
    responses={204: OpenApiResponse(description="Kategoriya o‘chirildi")}
)
class CategoryDeleteApiView(DestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()

        if request.user.role != request.user.RoleStatus.SUPERUSER:
            return Response({"detail": "Ruxsat yo‘q"}, status=status.HTTP_403_FORBIDDEN)

        self.perform_destroy(instance)
        return Response({"detail": "Kategoriya o‘chirildi"}, status=status.HTTP_204_NO_CONTENT)


@extend_schema(tags=['category'])
class CategoryUpdateApiView(UpdateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'

    def update(self, request, *args, **kwargs):
        user = self.request.user

        if user.role != user.RoleStatus.SUPERUSER:
            return Response({"detail": "Sizda ruxsat yo'q"}, status=status.HTTP_403_FORBIDDEN)

        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response({
            "detail": "Kategoriya o'zgartirildi",
            "data": serializer.data
        }, status.HTTP_200_OK)
