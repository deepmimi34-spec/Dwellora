from django.urls import path

from .views import (
    PropertyCreate,
    PropertyDeleteView,
    PropertyDetailView,
    PropertyListView,
    PropertyUpdate,
)

urlpatterns = [
    path('property/list/', PropertyListView.as_view(), name='property_list'),
    path('property/create/', PropertyCreate.as_view(), name='property_create'),
    path('property/<int:pk>/detail/', PropertyDetailView.as_view(), name='property_detail'),
    path('property/<int:pk>/update/', PropertyUpdate.as_view(), name='property_update'),
    path('property/<int:pk>/delete/', PropertyDeleteView.as_view(), name='property_delete'),
]
