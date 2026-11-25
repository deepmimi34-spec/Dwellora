from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated

from .forms import ProfileForm
from .serializers import ProfileSerializer
from .models import Profile


class ProfileCreate(generics.CreateAPIView):
    permission_classes = [AllowAny]
    form_class = ProfileForm
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()


class ProfileUpdate(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()

    def get_object(self):
        return self.request.user


class ProfileDelete(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()

    def get_object(self):
        return self.request.user


class ProfileList(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileSerializer

    def get_queryset(self):
        return Profile.objects.filter(pk=self.request.user.pk)
