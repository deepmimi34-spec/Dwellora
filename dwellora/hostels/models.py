from django.db import models
from property.models import Property


class HostelBuilding(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    hostel_name = models.CharField(max_length=20)
    town = models.CharField(max_length=20)


class HostelType(models.Model):
    PEOPLE_IN_A_ROOM_CHOICES = [
        ('1 in a room', '1 in a room'),
        ('2 in a room', '2 in a room'),
        ('3 in a room', '3 in a room'),
        ('4 in a room', '4 in a room'),
    ]

    hostel_building = models.ForeignKey(HostelBuilding, on_delete=models.CASCADE, related_name='hostel_building')
    name = models.CharField(max_length=20, choices=PEOPLE_IN_A_ROOM_CHOICES)
    bathrooms = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'hostel_type'
        verbose_name = 'Hostel Type'

    def __str__(self):
        return self.name


class HostelUnit(models.Model):
    STATUS_CHOICES = (
        ('available', 'available'),
        ('sold', 'sold'),
        ('rented', 'rented'),
    )

    hostel_type = models.ForeignKey(HostelType, on_delete=models.CASCADE)
    unit_name = models.CharField(max_length=20, help_text='unit name / room number')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')

    class Meta:
        db_table = 'hostel_unit'
        verbose_name = 'Hostel Unit'

    def __str__(self):
        return f'{self.status} - {self.unit_name}'
