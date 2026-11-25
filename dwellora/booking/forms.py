from django import forms
from django.forms import ModelForm

from .models import HostelBooking


class HostelBookingForm(ModelForm):
    class Meta:
        model = HostelBooking
        fields = ['hostel', 'start_date', 'end_date']
        widgets = {
            'start_date': forms.DateInput(
                attrs={'class': 'datepicker', 'type': 'date'}
            ),
            'end_date': forms.DateInput(
                attrs={'class': 'datepicker', 'type': 'date'}
            ),
        }
