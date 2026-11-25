from rest_framework import generics, permissions

from .forms import PropertyForm
from .serializers import PropertySerializer
from .models import Property


class PropertyListView(generics.ListAPIView):
    queryset = Property.objects.all().order_by('id')
    serializer_class = PropertySerializer
    permission_classes = (permissions.AllowAny,)


class PropertyCreate(generics.CreateAPIView):
    form_class = PropertyForm
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    # The current model has no owner/lister field. Keep creation staff-only
    # rather than accepting listings that cannot be attributed to an account.
    permission_classes = (permissions.IsAdminUser,)


class PropertyDetailView(generics.RetrieveAPIView):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    permission_classes = (permissions.AllowAny,)


class PropertyUpdate(generics.UpdateAPIView):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    permission_classes = (permissions.IsAdminUser,)


class PropertyDeleteView(generics.DestroyAPIView):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    form_class = PropertyForm
    permission_classes = (permissions.IsAdminUser,)
