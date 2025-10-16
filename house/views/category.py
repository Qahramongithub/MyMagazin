from django.core.cache import cache
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
from rest_framework import status, generics
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

        if self.request.user.role != User.RoleStatus.SUPERUSER:
            raise PermissionDenied("Sizda ruxsat yo'q", status.HTTP_403_FORBIDDEN)  # <-- mana bu to'g'ri

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

        if request.user.role != User.RoleStatus.SUPERUSER:
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


@extend_schema(
    tags=['category'],
    parameters=[
        OpenApiParameter(
            name='search',
            description='Kategoriya nomi bo‘yicha qidiruv (masalan: ?search=kitob)',
            required=False,
            type=str,
        ),
    ],
    responses={200: CategorySerializer(many=True)}
)
class CategorySearchApiView(APIView):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        warehouse_id = cache.get(f"user_{user.id}_warehouse_id")
        categories = Category.objects.filter(warehouse_id=warehouse_id)

        # GET orqali qidiruv so‘zi olish
        search = request.GET.get('search', '').strip()

        if search:
            queryset = categories.filter(name__icontains=search)
        else:
            queryset = categories
        serializer = CategorySerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
