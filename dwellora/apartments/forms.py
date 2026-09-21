from django import forms

from apartments.models import ApartmentBuilding, ApartmentType, ApartmentUnit


class ApartmentBuildingForm(forms.ModelForm):
    class Meta:
        model = ApartmentBuilding
        fields = '__all__'

        widgets = {
            'name' : forms.TextInput(attrs={'class':'form-control'}),
            'town' : forms.TextInput(attrs={'class':'form-control'}),
        }


class ApartmentTypeForm(forms.ModelForm):
    class Meta:
        model = ApartmentType
        fields = '__all__'

        widgets = {
            'name' : forms.TextInput(attrs={'class':'form-control'}),
            'living_room' : forms.BooleanField(),
            'bathroom' : forms.IntegerField(max_value=100),
            'rooms_with_bathrooms' : forms.IntegerField(),
        }

class ApartmentUnitForm(forms.ModelForm):
    class Meta:
        model = ApartmentUnit
        fields = '__all__'

        widgets = {
            'unit_name' : forms.TextInput(attrs={'class':'form-control'}),
            'apartment_status' : forms.Select(choices=ApartmentUnit.STATUS_CHOICES),
        }