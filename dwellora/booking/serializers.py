from rest_framework import serializers

from .models import HostelBooking


class HostelBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = HostelBooking
        fields = '__all__'