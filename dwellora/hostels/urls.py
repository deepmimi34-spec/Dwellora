from django.urls import path

from .views import HostelCreateView, HostelUnitUpdateView, HostelUnitListView, HostelUnitDetailView

urlpatterns = [
    path('create_bookings', HostelCreateView.as_view(), name='create_bookings'),
    path('update_booking', HostelUnitUpdateView.as_view(), name='update_booking'),
    path('list', HostelUnitListView.as_view(), name='list'),
    path('detail/<int:pk>/', HostelUnitDetailView.as_view(), name='detail'),
]