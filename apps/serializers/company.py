from rest_framework import serializers


class CompanyStatusSerializer(serializers.Serializer):
    warning = serializers.CharField(required=False)
    message = serializers.CharField(required=False)
    company = serializers.CharField(required=False)
    end_date = serializers.DateField(required=False, allow_null=True)
    error = serializers.CharField(required=False)
