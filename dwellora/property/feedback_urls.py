"""Not mounted from the active API URLConf until migrations are applied."""
from django.urls import path
from .feedback_views import (
    PropertyCommentCreate, PropertyCommentDelete, PropertyCommentList,
    PropertyCommentModerationUpdate, PropertyInteractionListCreate,
    PropertyInteractionStatusUpdate, PropertyInteractionVerify,
    PropertyReviewCreate, PropertyReviewList, PropertyReviewModerationUpdate,
)

urlpatterns = [
    path('interactions/', PropertyInteractionListCreate.as_view(), name='property-interactions'),
    path('interactions/<int:pk>/status/', PropertyInteractionStatusUpdate.as_view(), name='property-interaction-status'),
    path('interactions/<int:pk>/verify/', PropertyInteractionVerify.as_view(), name='property-interaction-verify'),
    path('<int:property_pk>/reviews/', PropertyReviewList.as_view(), name='property-review-list'),
    path('<int:property_pk>/reviews/create/', PropertyReviewCreate.as_view(), name='property-review-create'),
    path('reviews/<int:pk>/moderation/', PropertyReviewModerationUpdate.as_view(), name='property-review-moderation'),
    path('<int:property_pk>/comments/', PropertyCommentList.as_view(), name='property-comment-list'),
    path('<int:property_pk>/comments/create/', PropertyCommentCreate.as_view(), name='property-comment-create'),
    path('comments/<int:pk>/moderation/', PropertyCommentModerationUpdate.as_view(), name='property-comment-moderation'),
    path('comments/<int:pk>/delete/', PropertyCommentDelete.as_view(), name='property-comment-delete'),
]
