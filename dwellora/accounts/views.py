from rest_framework import generics
from rest_framework.permissions import IsAuthenticated


from .forms import ProfileForm
from .serializers import ProfileSerializer
from .models import Profile


class ProfileCreate(generics.CreateAPIView):
    form_class = ProfileForm
    model_create = Profile
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()


class ProfileUpdate(generics.RetrieveUpdateAPIView):
        permission_classes = [IsAuthenticated]
        serializer_class = ProfileSerializer
        model_update = Profile
        queryset = Profile.objects.all()


class ProfileDelete(generics.DestroyAPIView):
        permission_classes = [IsAuthenticated]
        serializer_class = ProfileSerializer
        model_delete = Profile
        queryset = Profile.objects.all()


class ProfileList(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()
    model_list = Profile








# Create your views here.
