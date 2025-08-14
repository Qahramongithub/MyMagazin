from django.forms import IntegerField
from rest_framework import serializers

from apps.models import Warehouse


class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = ['id', 'location', 'name']
        read_only_fields = ['id']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

#
# class WarehouseDetailSerializer(WarehouseSerializer):
#     warehouses = IntegerField(
#
#     )
