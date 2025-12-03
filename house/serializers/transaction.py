from rest_framework import serializers

from house.models import Transactions


class TransactionModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transactions
        fields = ('name','category','description','price','status',)
