from django.contrib.auth.hashers import make_password
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.serializers.user import PasswordSerializer


@extend_schema(
    tags=["password"],
    request=PasswordSerializer
)
class Password(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PasswordSerializer

    def post(self, request):
        serializer = PasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        password = serializer.validated_data['password']

        user = request.user  # request.user bu User obyekti
        user.password = make_password(password)  # parolni hash qilib saqlaymiz
        user.save()

        return Response({"success": "Password updated successfully"}, status=status.HTTP_200_OK)


from rest_framework_simplejwt.views import TokenObtainPairView
from apps.serializers.user import MyTokenObtainPairSerializer


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
