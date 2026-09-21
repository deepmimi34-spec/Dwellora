from django.db import models
from accounts.models import Profile

class Service(models.Model):
    SERVICE_CHOICES = (
        ('Landlord / Landlady', 'Landlord / Landlady'),
        ('Real-estate agent', 'Real-estate agent'),
        ('Hotel owner', 'Hotel owner'),
        ('Hostel administrator', 'Hostel administrator'),
        ('Architect', 'Architect'),
        ('Builder / Mason', 'Builder / Mason'),
        ('Plumber', 'Plumber'),
        ('Painter', 'Painter'),
        ('Electrician', 'Electrician'),
        ('Welder', 'Welder'),
        ('Cleaner', 'Cleaner'),
        ('Moving service', 'Moving service'),
        ('Landscaper', 'Landscaper'),
        ('Security installer', 'Security installer'),
        ('AC technicians', 'AC technicians'),
        ('Other service providers', 'Other service providers'),
    )
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)
    service_type = models.CharField(choices=SERVICE_CHOICES, default='Landlord / landlady', max_length=100)
    description = models.TextField()

    class Meta:
        db_table = 'service'
        verbose_name = 'service'
        verbose_name_plural = 'services'
# Create your models here.
