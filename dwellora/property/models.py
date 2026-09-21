from django.db import models


class Property(models.Model):

    PROPERTY_CHOICES = [
        ('Apartment', 'Apartment'),
        ('Hotel', 'Hotel'),
        ('House', 'House'),
        ('Hostel', 'Hostel'),
    ]

    LOCATION_CHOICES = [
        ('Ahafo', 'Ahafo'),
        ('Ashanti', 'Ashanti'),
        ('Bono', 'Bono'),
        ('Bono East', 'Bono East'),
        ('Central', 'Central'),
        ('Eastern', 'Eastern'),
        ('Greater Accra', 'Greater Accra'),
        ('North East', 'North East'),
        ('Northern', 'Northern'),
        ('Oti', 'Oti'),
        ('Savannah', 'Savannah'),
        ('Upper East', 'Upper East'),
        ('Upper West', 'Upper West'),
        ('Volta', 'Volta'),
        ('Western', 'Western'),
        ('Western North', 'Western North'),
    ]

    title = models.CharField(max_length=100)

    property_type = models.CharField(
        max_length=20,
        choices=PROPERTY_CHOICES
    )

    region = models.CharField(
        max_length=50,
        choices=LOCATION_CHOICES
    )
    city = models.CharField(max_length=50, blank=True, help_text='e.g., Kumasi, Accra')

    furnished = models.BooleanField(default=False)

    parking = models.BooleanField(default=False)

    water_available = models.BooleanField(default=False)

    internet_available = models.BooleanField(default=False)

    kitchen_available = models.BooleanField(default=False)



    class Meta:
        db_table = 'property'
        verbose_name = 'Property'

    def __str__(self):
        return self.title

    def is_property_complete(self):
        return bool(
            self.title
            and self.location
        )


