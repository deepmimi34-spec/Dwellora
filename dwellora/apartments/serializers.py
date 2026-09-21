from rest_framework import serializers
from .models import ApartmentUnit, ApartmentBuilding, ApartmentType

class ApartmentUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApartmentUnit
        fields = '__all__'

class ApartmentBuildingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApartmentBuilding
        fields = '__all__'

class ApartmentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApartmentType
        fields = '__all__'



