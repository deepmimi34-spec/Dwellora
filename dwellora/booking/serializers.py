from rest_framework import serializers

from .models import HostelBooking


class HostelBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = HostelBooking
        fields = '__all__'
        read_only_fields = ('id', 'created_at')

    def validate_hostel(self, value):
        if value.status != 'available':
            raise serializers.ValidationError(
                'This hostel unit is not currently available for booking.'
            )
        return value

    def validate(self, attrs):
        start_date = attrs.get(
            'start_date',
            getattr(self.instance, 'start_date', None),
        )
        end_date = attrs.get(
            'end_date',
            getattr(self.instance, 'end_date', None),
        )

        if start_date and end_date and end_date <= start_date:
            raise serializers.ValidationError({
                'end_date': 'The end date must be after the start date.'
            })

        return attrs
