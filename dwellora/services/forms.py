from django import forms
from django.forms import ModelForm
from .models import Service

class ServiceForm(ModelForm):
    class Meta:
        model = Service
        fields = '__all__'

        widgets = {
            'service_type': forms.TypedMultipleChoiceField(choices=Service.SERVICE_CHOICES,),
            'description': forms.Textarea(attrs={'rows': 5}),
        }