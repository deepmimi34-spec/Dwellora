from django.urls import path

from .views import (
    ServiceCreate,
    ServiceDelete,
    ServiceDetail,
    ServiceList,
    ServiceUpdate,
)

urlpatterns = [
    path('', ServiceList.as_view(), name='service_list'),
    path('create_service/', ServiceCreate.as_view(), name='service_create'),
    path('create_service/<int:pk>/', ServiceDetail.as_view(), name='service_detail'),
    path('update_service/<int:pk>/', ServiceUpdate.as_view(), name='service_update'),
    path('delete_service/<int:pk>/', ServiceDelete.as_view(), name='service_delete'),
]
