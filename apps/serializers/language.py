from rest_framework import serializers


class ChangeLanguageSerializer(serializers.Serializer):
    language = serializers.ChoiceField(choices=[("en", "English"), ("uz", "Uzbek"), ("ru", "Russian")])
