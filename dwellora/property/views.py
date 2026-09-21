from django.contrib.auth import get_user_model
from rest_framework import generics, permissions

from .forms import PropertyForm
from .serializers import PropertySerializer
from .models import Property

User = get_user_model()

# Properties of agents and landlords
class PropertyCreate(generics.CreateAPIView):
    form_class = PropertyForm
    model_class = Property
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = PropertySerializer




class PropertyDetailView(generics.ListAPIView):
    model = Property
    serializer_class = PropertySerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = Property.objects.all()


class PropertyUpdate(generics.UpdateAPIView):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    model_class = Property
    permission_classes = (permissions.IsAuthenticated,)



class PropertyDeleteView(generics.DestroyAPIView):
    model = Property
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = PropertySerializer
    queryset = Property.objects.all()
    form_class = PropertyForm




# Create your views here.


