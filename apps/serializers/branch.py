from rest_framework import serializers


class ProductTransferItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)


class BulkTransferSerializer(serializers.Serializer):
    to_warehouse = serializers.IntegerField()
    items = ProductTransferItemSerializer(many=True)

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("Items list cannot be empty.")
        return value

