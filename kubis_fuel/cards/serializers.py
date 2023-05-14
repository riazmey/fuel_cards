import datetime
from rest_framework import serializers
from .models import SiteBalance


class SiteBalanceSerializer(serializers.Serializer):
    site_id = serializers.IntegerField()
    date = serializers.DateTimeField()
    balance = serializers.FloatField(read_only=True)
    credit = serializers.FloatField(read_only=True)
    available = serializers.FloatField(read_only=True)

    def create(self, validated_data):
        return SiteBalance.objects.create(**validated_data)

    def update(self, instance, validated_data):
        pass
