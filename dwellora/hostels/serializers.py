from rest_framework import serializers
from .models import HostelUnit

class HostelUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = HostelUnit
        fields = '__all__'