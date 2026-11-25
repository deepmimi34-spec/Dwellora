from django import forms
from django.forms import ModelForm

from .models import Service


class ServiceForm(ModelForm):
    class Meta:
        model = Service
        fields = ['service_type', 'description']
        widgets = {
            'service_type': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 5}
            ),
        }
