from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework.generics import CreateAPIView, ListAPIView, UpdateAPIView, DestroyAPIView

from .forms import HostelBookingForm
from .models import HostelBooking
from .serializers import HostelBookingSerializer


class HostelBookingView(ListAPIView):
    queryset = HostelBooking.objects.all()
    model = HostelBooking
    serializer_class = HostelBookingSerializer
    form_class = HostelBookingForm
    context_object_name = 'hostel_booking'


class HostelBookingCreateView(LoginRequiredMixin, CreateAPIView):
    model = HostelBooking
    serializer_class = HostelBookingSerializer
    FormClass = HostelBookingForm
    queryset = HostelBooking.objects.all()


class HostelBookingUpdateView(LoginRequiredMixin, UpdateAPIView):
    model = HostelBooking
    serializer_class = HostelBookingSerializer
    form_class = HostelBookingForm
    queryset = HostelBooking.objects.all()

class HostelBookingDestroyView(DestroyAPIView):
    model = HostelBooking
    serializer_class = HostelBookingSerializer
    form_class = HostelBookingForm
    queryset = HostelBooking.objects.all()
# Create your views here.
