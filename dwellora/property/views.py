from rest_framework import generics, permissions

from .forms import PropertyForm
from .serializers import PropertySerializer
from .models import Property


class PropertyCreate(generics.CreateAPIView):
    form_class = PropertyForm
    model_class = Property
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = PropertySerializer


class PropertyDetailView(generics.RetrieveAPIView):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class PropertyUpdate(generics.UpdateAPIView):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    model_class = Property
    # Until listings have an explicit owner/lister relationship, only staff may edit.
    permission_classes = (permissions.IsAdminUser,)


class PropertyDeleteView(generics.DestroyAPIView):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    form_class = PropertyForm
    # Until listings have an explicit owner/lister relationship, only staff may delete.
    permission_classes = (permissions.IsAdminUser,)
