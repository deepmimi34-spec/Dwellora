from django.urls import path
from .views import HotelListAPIView, HotelCreateAPIView, HotelDeleteAPIView, HotelDetailAPIView, HotelUpdateAPIView


urlpatterns = [
    path('hostel/list/', HotelListAPIView.as_view()),
    path('hostel/create/', HotelCreateAPIView.as_view()),
    path('hostel/delete/', HotelDeleteAPIView.as_view()),
    path('hostel/detail/', HotelDetailAPIView.as_view()),
    path('hostel/update/', HotelUpdateAPIView.as_view()),
]