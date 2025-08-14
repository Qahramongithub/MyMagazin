from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

from apps.serializers.company import CompanyStatusSerializer
from apps.models import User


class CompanyStatusAPIView(APIView):
    serializer_class = CompanyStatusSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user

        if not user.is_authenticated or user.role != User.RoleStatus.SUPERUSER:
            return Response({}, status=status.HTTP_204_NO_CONTENT)

        company = User.objects.filter(role=User.RoleStatus.SUPERUSER).first()

        if not company:
            return Response(
                {"error": "Kompaniya topilmadi"},
                status=status.HTTP_404_NOT_FOUND
            )

        now = timezone.now().date()

        if company.superuser_end_date and now > company.superuser_end_date:
            company.is_active = False  # 👉 Bloklash
            company.save(update_fields=['is_active'])  # 👉 Saqlash
            data = {
                "warning": "Kompaniya muddati tugagan!",
                "company": company.username,
                "end_date": company.superuser_end_date
            }
        else:
            data = {
                "message": "Kompaniya faol.",
                "company": company.username,
                "end_date": company.superuser_end_date
            }

        serializer = self.serializer_class(data)
        return Response(serializer.data, status=status.HTTP_200_OK)
