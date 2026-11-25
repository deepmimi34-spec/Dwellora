from rest_framework import generics, permissions, serializers

from .models import Service
from .serializers import ServiceSerializer


class ServiceList(generics.ListAPIView):
    queryset = Service.objects.select_related('profile').order_by('id')
    serializer_class = ServiceSerializer
    permission_classes = [permissions.AllowAny]


class ServiceCreate(generics.CreateAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        if Service.objects.filter(profile=self.request.user).exists():
            raise serializers.ValidationError({
                'service': 'Your provider profile already exists.'
            })
        serializer.save(profile=self.request.user)


class ServiceDetail(generics.RetrieveAPIView):
    queryset = Service.objects.select_related('profile')
    serializer_class = ServiceSerializer
    permission_classes = [permissions.AllowAny]


class ServiceUpdate(generics.UpdateAPIView):
    serializer_class = ServiceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Service.objects.filter(profile=self.request.user)


class ServiceDelete(generics.DestroyAPIView):
    serializer_class = ServiceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Service.objects.filter(profile=self.request.user)
