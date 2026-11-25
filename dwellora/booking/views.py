from rest_framework import generics, permissions

from .models import HostelBooking
from .serializers import HostelBookingSerializer


# Booking ownership is not yet represented in the current schema.
# Keep these operational endpoints staff-only until bookings are linked
# to the authenticated customer and permission-tested.
class HostelBookingView(generics.ListAPIView):
    queryset = HostelBooking.objects.select_related(
        'hostel',
        'hostel__hostel_type',
        'hostel__hostel_type__hostel_building',
    )
    serializer_class = HostelBookingSerializer
    permission_classes = [permissions.IsAdminUser]


class HostelBookingCreateView(generics.CreateAPIView):
    queryset = HostelBooking.objects.all()
    serializer_class = HostelBookingSerializer
    permission_classes = [permissions.IsAdminUser]


class HostelBookingUpdateView(generics.UpdateAPIView):
    queryset = HostelBooking.objects.all()
    serializer_class = HostelBookingSerializer
    permission_classes = [permissions.IsAdminUser]


class HostelBookingDestroyView(generics.DestroyAPIView):
    queryset = HostelBooking.objects.all()
    serializer_class = HostelBookingSerializer
    permission_classes = [permissions.IsAdminUser]
