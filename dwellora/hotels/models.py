from django.db import models
from property.models import Property


class HotelBuilding(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='hostel_building')
    name = models.CharField(max_length=20, unique=True)
    specifies_town = models.CharField(max_length=20)

    class Meta:
        db_table = 'hostel_building'
        verbose_name = 'Hotel Building'


class HotelType(models.Model):
    BEDROOM_CHOICES = (
        ('1 Bedroom', '1 Bedroom'),
        ('2 Bedroom', '2 Bedroom'),
        ('3 Bedroom', '3 Bedroom'),
        ('4 Bedroom', '4 Bedroom'),
        ('5 Bedroom', '5 Bedroom'),
        ('6 Bedroom', '6 Bedroom'),
        ('7+ Bedroom', '7+ Bedroom'),
    )
    hostel_building = models.ForeignKey(HotelBuilding, on_delete=models.CASCADE, related_name='hostel_type')
    name = models.CharField(max_length=20, choices=BEDROOM_CHOICES)
    living_rooms = models.IntegerField()
    kitchen_rooms = models.IntegerField()
    bathrooms = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'hotel_type'
        verbose_name = 'Hotel Type'


class HotelUnit(models.Model):
    STATUS_CHOICES = (
        ('available', 'available'),
        ('sold', 'sold'),
        ('rented', 'rented'),
    )

    apartment_type = models.ForeignKey(HotelType, on_delete=models.CASCADE, related_name='apartment_units')
    unit_name = models.CharField(max_length=20, help_text='Name of the unit / room number')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    class Meta:
        db_table = 'hotel_unit'
        verbose_name = 'Hotel Unit'
