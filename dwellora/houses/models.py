from django.db import models

from property.models import Property

class HousesBuilding(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='property_Houses')
    address = models.CharField( max_length=50, help_text='e.g., AK-039-8164')
    town = models.CharField( max_length=50, help_text='e.g., Santasi, Patasi ')

    class Meta:
        db_table = 'houses_building'
        verbose_name = 'Houses Building'

    def __str__(self):
        return f'{self.town} - {self.address}'


class HousesType(models.Model):
    property_house = models.ForeignKey(HousesBuilding, on_delete=models.CASCADE, related_name='property_Houses')
    rooms_per_house = models.PositiveIntegerField(max_length=20)
    rooms_with_bathrooms = models.PositiveIntegerField(max_length=20)
    living_rooms = models.BooleanField(default=False)
    bathrooms = models.PositiveIntegerField(max_length=20, default=1)


    class Meta:
        db_table = 'houses_type'
        verbose_name = 'Houses Type'


class HousesUnit(models.Model):
    STATUS_CHOICES = (
        ('available', 'available'),
        ('sold', 'sold'),
        ('rented', 'rented'),
    )
    house_type = models.ForeignKey(HousesType, on_delete=models.CASCADE, related_name='house_type_Houses')
    status = models.CharField( max_length=20, choices=STATUS_CHOICES, default='available')


    class Meta:
        db_table = 'hostel_unit'
        verbose_name = 'Houses Unit'

# Create your models here.
