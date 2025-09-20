from django.conf import settings
from drf_spectacular.utils import extend_schema
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from django.utils import translation

from apps.serializers.language import ChangeLanguageSerializer


@extend_schema(
    tags=["language"],
    request=ChangeLanguageSerializer,  # Swaggerga request schema
    responses={200: ChangeLanguageSerializer}  # Swaggerga javob schema
)
class ChangeLanguageAPIView(GenericAPIView):
    serializer_class = ChangeLanguageSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        lang_code = serializer.validated_data["language"]

        translation.activate(lang_code)
        response = Response({
            "message": "Til o'zgartirildi",
            "language": lang_code
        })
        # Cookie muddatini katta qilib qo'yamiz (10 yil)
        response.set_cookie(
            settings.LANGUAGE_COOKIE_NAME,
            lang_code,
            max_age=60 * 60 * 24 * 365 * 10  # 10 yil
        )
        return response
