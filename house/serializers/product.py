from rest_framework import serializers

from house.models import Product, Category


class ProductModelSerializer(serializers.ModelSerializer):
    categories = serializers.SlugRelatedField(
        slug_field='name',
        queryset=Category.objects.all()
    )
    status = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ('warehouse',)

    def validate(self, data):
        price = data.get('price')
        base_price = data.get('base_price')
        discount_price = data.get('discount_price')

        if price is None or base_price is None or discount_price is None:
            raise serializers.ValidationError("Barcha qiymatlar to‘ldirilishi kerak.")

        if price >= base_price:
            if discount_price > price:
                raise serializers.ValidationError("Chegirma narxi tovar narxidan katta bo‘lishi mumkin emas.")
        else:
            raise serializers.ValidationError("Mahsulot narxi  sotiladigan narxidan yuqori bulishi mumkin emas !")

        return data

    def create(self, validated_data):
        return Product.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
