from django.urls import path
from .views import ProductFeedbackListCreate, ProductFeedbackTriage

urlpatterns = [
    path("", ProductFeedbackListCreate.as_view(), name="product-feedback-list-create"),
    path("<int:pk>/triage/", ProductFeedbackTriage.as_view(), name="product-feedback-triage"),
]
