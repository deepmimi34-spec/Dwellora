from django.shortcuts import render
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView, UpdateAPIView
from .models import HostelUnit
from .forms import HostelUnitForm
from .serializers import HostelUnitSerializer


class HostelCreateView(CreateAPIView):
    model = HostelUnit
    form_class = HostelUnitForm
    serializer_class = HostelUnitSerializer
    queryset = HostelUnit.objects.all()


class HostelUnitListView(ListAPIView):
    queryset = HostelUnit.objects.all()
    model = HostelUnit
    form_class = HostelUnitForm
    serializer_class = HostelUnitSerializer


class HostelUnitDetailView(RetrieveAPIView):
    queryset = HostelUnit.objects.all()
    model = HostelUnit
    serializer_class = HostelUnitSerializer
    form_class = HostelUnitForm


class HostelUnitUpdateView(UpdateAPIView):
    model = HostelUnit
    form_class = HostelUnitForm
    serializer_class = HostelUnitSerializer
    queryset = HostelUnit.objects.all()
# Create your views here.
