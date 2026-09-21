from django.shortcuts import render
from rest_framework.generics import ListAPIView, CreateAPIView, UpdateAPIView, DestroyAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny

from hotels.forms import HotelForm
from hotels.models import Hotel
from hotels.serializers import HotelSerializer


class HotelListAPIView(ListAPIView):
    queryset = Hotel.objects.all()
    serializer_class = HotelSerializer
    model_class = Hotel
    permission_classes = (AllowAny,)


class HotelCreateAPIView(CreateAPIView):
    queryset = Hotel.objects.all()
    serializer_class = HotelSerializer
    model_class = Hotel
    form_class = HotelForm
    permission_classes = (IsAuthenticated,)


class HotelDetailAPIView(RetrieveAPIView):
    queryset = Hotel.objects.all()
    serializer_class = HotelSerializer
    model_class = Hotel
    permission_classes = (IsAuthenticated,)

class HotelUpdateAPIView(UpdateAPIView):
    queryset = Hotel.objects.all()
    serializer_class = HotelSerializer
    model_class = Hotel
    permission_classes = (IsAuthenticated,)


class HotelDeleteAPIView(DestroyAPIView):
    queryset = Hotel.objects.all()
    serializer_class = HotelSerializer
    model_class = Hotel
    permission_classes = (IsAuthenticated,)
# Create your views here.
