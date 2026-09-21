from django.urls import path
from .views import ServiceList, ServiceDetail, ServiceUpdate, ServiceDelete

urlpatterns = [
    path('create_service/', ServiceList.as_view()),
    path('create_service/<int:pk>/', ServiceDetail.as_view()),
    path('update_service/<int:pk>/', ServiceUpdate.as_view()),
    path('delete_service/<int:pk>/', ServiceDelete.as_view()),
]