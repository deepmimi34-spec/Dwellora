from rest_framework import generics, permissions

from .forms import ServiceForm
from .models import Service
from .serializers import ServiceSerializer


class ServiceList(generics.CreateAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    form_class = ServiceForm
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class ServiceDetail(generics.RetrieveUpdateAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    model_form = Service
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class ServiceUpdate(generics.RetrieveUpdateAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    form_class = ServiceForm
    model_form = Service
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

class ServiceDelete(generics.RetrieveUpdateAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    model_form = Service
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)




# Create your views here.
