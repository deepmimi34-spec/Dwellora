from django import forms
from django.forms import ModelForm

from .models import Property


class PropertyForm(ModelForm):
    class Meta:
        model = Property
        fields = [
            'title',
            'property_type',
            'region',
            'city',
            'furnished',
            'parking',
            'water_available',
            'internet_available',
            'kitchen_available',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'property_type': forms.Select(attrs={'class': 'form-control'}),
            'region': forms.Select(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'furnished': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'parking': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'water_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'internet_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'kitchen_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'property_type': 'Property type',
            'region': 'Region',
        }
