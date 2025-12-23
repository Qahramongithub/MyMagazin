from decimal import Decimal

from django.core.cache import cache
from django.shortcuts import get_object_or_404
from rest_framework import serializers
import telebot
from house.models import Order, OrderItem
from apps.models import Warehouse
import os


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_unit = serializers.CharField(source='product.unit', read_only=True)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    discount_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'product_unit', 'quantity', 'price', 'discount_price']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, source='orderitem_set')

    class Meta:
        model = Order
        fields = ['id', 'created_at', 'items', 'warehouse']
        read_only_fields = ['warehouse']

    def create(self, validated_data):
        items_data = validated_data.pop('orderitem_set')
        user = self.context['request'].user

        warehouse_id = cache.get(f"user_{user.id}_warehouse_id")
        if not warehouse_id:
            raise serializers.ValidationError("Warehouse ID topilmadi. Iltimos, user uchun keshni tekshiring.")

        warehouse = get_object_or_404(Warehouse, pk=warehouse_id)
        validated_data['warehouse'] = warehouse

        order = Order.objects.create(**validated_data)

        for item_data in items_data:
            product = item_data['product']
            quantity = item_data['quantity']

            if product.quantity < quantity:
                raise serializers.ValidationError(
                    f"{product.name} mahsuloti uchun yetarli quantity ({product.quantity}) mavjud emas."
                )

            item_data['base_price'] = product.base_price
            item_data['price'] = product.discount_price if product.discount_price > 0 else product.price

            OrderItem.objects.create(order=order, **item_data)

            product.quantity -= quantity
            product.save(update_fields=['quantity'])

        return order


class OrderExelSerializer(serializers.ModelSerializer):
    start_date = serializers.DateTimeField(source='created_at', read_only=True)
    end_date = serializers.DateTimeField(source='created_at', read_only=True)

    class Meta:
        model = Order
        fields = '__all__'
