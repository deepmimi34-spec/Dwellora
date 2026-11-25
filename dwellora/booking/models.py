from django.db import models
from hostels.models import HostelUnit


class HostelBooking(models.Model):
    hostel = models.ForeignKey(HostelUnit, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f'{self.hostel.unit_name} - '
            f'{self.start_date:%Y-%m-%d} to {self.end_date:%Y-%m-%d}'
        )
