from django import forms

from hostels.models import HostelUnit


class HostelUnitForm(forms.ModelForm):
    class Meta:
        model = HostelUnit
        fields = '__all__'

        widgets = {
            'floor_room': forms.IntegerField(),
            'price': forms.IntegerField(),
            'description': forms.CharField()
        }