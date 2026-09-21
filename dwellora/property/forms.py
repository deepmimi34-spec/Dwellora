from django import forms
from django.forms import ModelForm

from .models import Property, UniversityHostel, House, Hotel, Apartments


class PropertyForm(ModelForm):
    class Meta:
        model = Property
        fields = '__all__'

        widgets = {
            'title' : forms.TextInput(attrs={'class': 'form-control'}),
            'property_type' : forms.BooleanField(required=False, initial=True, widget=forms.CheckboxInput(attrs={'class': 'form-control'})),
            'location' : forms.TypedChoiceField(required=False, coerce=lambda x:x == 'True', widget=forms.Select(attrs={'class': 'form-control'})),
            'price' : forms.NumberInput(attrs={'class': 'form-control'}),
            'number_of_rooms' : forms.NumberInput(attrs={'class': 'form-control'}),
            'number_of_bathrooms' : forms.NumberInput(attrs={'class': 'form-control'}),
            'parking' : forms.BooleanField(required=False, initial=True, widget=forms.CheckboxInput(attrs={'class': 'form-control'})),
            'water_available' : forms.BooleanField(required=False, initial=True, widget=forms.CheckboxInput(attrs={'class': 'form-control'})),
            'internet_available' : forms.BooleanField(required=False, initial=True, widget=forms.CheckboxInput(attrs={'class': 'form-control'})),
            'kitchen_available' : forms.BooleanField(required=False, initial=True, widget=forms.CheckboxInput(attrs={'class': 'form-control'})),
            'description' : forms.Textarea(attrs={'class': 'form-control'}),
            'is_available' : forms.BooleanField(required=False, initial=True, widget=forms.CheckboxInput(attrs={'class': 'form-control'})),
        }

        label = {
            'property_type' : 'Property',
            'location' : 'Location',
            'price' : 'Price',
        }



class Hostel(ModelForm):
    class Meta:
        model = UniversityHostel
        fields = '__all__'

        widgets = {
            'floor' : forms.TypedChoiceField(required=False, coerce=lambda x:x == 'True', widget=forms.Select(attrs={'class': 'form-control'})),
            'number_in_a_room' : forms.TypedChoiceField(required=False, widget=forms.Select(attrs={'class': 'form-control'})),
            'bathroom' : forms.TypedChoiceField(required=False,  widget=forms.Select(attrs={'class': 'form-control'})),
            'distance_from_university' : forms.NumberInput(attrs={'class': 'form-control'}),
            'specific_place' : forms.TextInput(attrs={'class': 'form-control'}),
            'transportation' : forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-control'})),
        }


class HouseForm(ModelForm):
    class Meta:
        model = House
        fields = '__all__'

        widgets = {
            'town' : forms.TextInput(attrs={'class': 'form-control'}),
            'square_meters' : forms.NumberInput(attrs={'class': 'form-control'}),
            'outdooring_facilities': forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-control'})),
        }

class Hotels(ModelForm):
    class Meta:
        model = Hotel
        fields = '__all__'

        widgets = {
            'town' : forms.TextInput(attrs={'class': 'form-control'}),
            'restaurants' : forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-control'})),
            'outdooring_facilities': forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-control'})),
        }

class Apartment(ModelForm):
    class Meta:
        model = Apartments
        fields = '__all__'

        widgets = {
            'town' : forms.TextInput(attrs={'class': 'form-control'}),
            'road_type' : forms.TypedChoiceField(required=True, coerce=lambda x:x == 'True', widget=forms.Select(attrs={'class': 'form-control'})),
        }