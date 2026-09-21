from django.urls import path
from .views import HostelBookingView, HostelBookingCreateView, HostelBookingDestroyView, HostelBookingUpdateView

urlpatterns = [
    path('hostel_booking/', HostelBookingCreateView.as_view(), name='hostel_booking_create'),
    path('hostel_update/', HostelBookingUpdateView.as_view(), name='hostel_booking_update'),
    path('hostel_view/', HostelBookingView.as_view(), name='hostel_booking_view'),
    path('hostel_delete/', HostelBookingDestroyView.as_view(), name='hostel_booking_destroy'),
]