from rest_framework import serializers

from house.models import Transactions


class TransactionModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transactions
        fields = ('id', 'name', 'category', 'description', 'price', 'status', 'created_at')
        read_only_fields = ('created_at', 'id',)
