from django.forms import DateField
from rest_framework import serializers
from rest_framework.fields import FileField


class ExelSerializer(serializers.Serializer):
    start_date = DateField()
    end_date = DateField()


class AnaliticaSerializer(serializers.Serializer):
    exel = FileField()

