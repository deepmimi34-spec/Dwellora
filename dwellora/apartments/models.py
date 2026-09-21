from django.db import models
from property.models import Property


class ApartmentBuilding(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='property_building')
    name = models.CharField(max_length=50, help_text='The name of the apartment')
    town = models.CharField(max_length=50, help_text='The town of the apartment')

    class Meta:
        db_table = 'apartment_building'
        verbose_name = 'apartment building'
        ordering = ['property']

    def __str__(self):
        return f'{self.property} - {self.name} - {self.town}'


class ApartmentType(models.Model):
    APARTMENT_TYPE_CHOICES = [
        ('1 bedroom apartment', '1 bedroom apartment'),
        ('2 bedroom apartment', '2 bedroom apartment'),
        ('3 bedroom apartment', '3 bedroom apartment'),
        ('4 bedroom apartment', '4 bedroom apartment'),
        ('5 bedroom apartment', '5 bedroom apartment'),
        ('6 bedroom apartment', '6 bedroom apartment'),
        ('7 bedroom apartment', '7 bedroom apartment'),
    ]

    property_building = models.ForeignKey(ApartmentBuilding, on_delete=models.CASCADE, related_name='property_building')
    name = models.CharField(max_length=50, choices=APARTMENT_TYPE_CHOICES)
    living_rooms = models.BooleanField(default=True)
    bathrooms = models.PositiveIntegerField(default=1)
    rooms_with_bathrooms = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'apartment_type'

    def __str__(self):
        return f'{self.property_building} - {self.name} - {self.living_rooms}'

class ApartmentUnit(models.Model):
    STATUS_CHOICES = (
        ('available', 'available'),
        ('sold', 'sold'),
        ('rented', 'rented'),
    )

    apartment_unit = models.ForeignKey(ApartmentBuilding, on_delete=models.CASCADE, related_name='apartment_units')
    unit_room = models.PositiveIntegerField(help_text='Apartment room number', blank=True, null=True)
    apartment_status = models.CharField(choices=STATUS_CHOICES, max_length=50, default='available')

    class Meta:
        db_table = 'apartment_unit'
        verbose_name = 'apartment unit'


    def __str__(self):
        return f'{self.unit_room} - {self.apartment_status}'


# Create your models here.
