from rest_framework import serializers

from apps.models import User


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'role')

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Bu username allaqachon mavjud.")
        return value

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class PasswordSerializer(serializers.Serializer):
    password = serializers.CharField()
    confirm_password = serializers.CharField()

    def validate(self, data):
        password = data.get('password')
        confirm_password = data.get('confirm_password')
        if password != confirm_password:
            raise serializers.ValidationError("Password and Confirm Password don't match.")
        else:
            if len(password) < 8:
                raise serializers.ValidationError("Password must be at least 8 characters long.")
            return data


from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Token ichiga qo‘shimcha maʼlumot (claims)
        token['user_id'] = user.id
        token['username'] = user.username
        token['role'] = user.role
        token['is_superuser'] = user.role == User.RoleStatus.SUPERUSER

        return token
