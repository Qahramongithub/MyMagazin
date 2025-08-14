from rest_framework import serializers
from rest_framework.response import Response
from rest_framework import status
from django.core.cache import cache  # Redis uchun
from house.models import Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            'id',
            'name',
        ]
        read_only_fields = ['warehouse_id']

    def create(self, validated_data):
        user = self.context['request'].user
        warehouse_id = cache.get(f"user_{user.id}_warehouse_id")
        validated_data['warehouse_id'] = warehouse_id
        if not user.is_authenticated:
            return Response({
                status.HTTP_401_UNAUTHORIZED
            })

        return Category.objects.create(**validated_data)

    def update(self, instance, validated_data):
        user = self.context['request'].user
        if not user.is_authenticated:
            raise serializers.ValidationError("Foydalanuvchi autentifikatsiyadan o'tmagan.")

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

    def delete(self, instance):
        user = self.context['request'].user
        if not user.is_authenticated:
            return Response({
                status.HTTP_401_UNAUTHORIZED
            })
        return Category.objects.filter(id=instance.id).delete()
