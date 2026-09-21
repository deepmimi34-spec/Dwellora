from django.forms import ModelForm, DateInput

from booking.models import HostelBooking


class HostelBookingForm(ModelForm):
     class Meta:
        model = HostelBooking
        fields = '__all__'
        exclude = ('first_name', 'last_name', )

        widgets = {
            'start_date': DateInput(attrs={'class': 'datepicker'}),
            'end_date': DateInput(attrs={'class': 'datepicker'}),
        }