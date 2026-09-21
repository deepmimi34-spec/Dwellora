from django import forms
from .models import Hotel

class HotelForm(forms.ModelForm):
    class Meta:
        model = Hotel
        fields = '__all__'

        widgets = {
            'hotel_address': forms.TextInput(attrs={'class': 'form-control'}),
            'hotel_name': forms.TextInput(attrs={'class': 'form-control'}),
            'number_of_rooms': forms.IntegerField(),
        }