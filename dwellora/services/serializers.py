from rest_framework import serializers

from .models import Service


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ('id', 'profile', 'service_type', 'description')
        read_only_fields = ('id', 'profile')
