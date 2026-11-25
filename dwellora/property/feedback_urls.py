"""Feedback endpoints are intentionally not included in the active API URLConf.

Mount this URL set only after the reviewed migrations for PropertyInteraction,
PropertyReview and PropertyComment have been applied to the target database.
"""
from django.urls import path

from .feedback_views import (
    PropertyCommentCreate,
    PropertyCommentDelete,
    PropertyCommentList,
    PropertyCommentModerationUpdate,
    PropertyReviewCreate,
    PropertyReviewList,
    PropertyReviewModerationUpdate,
)

urlpatterns = [
    path('<int:property_pk>/reviews/', PropertyReviewList.as_view(), name='property-review-list'),
    path('<int:property_pk>/reviews/create/', PropertyReviewCreate.as_view(), name='property-review-create'),
    path('reviews/<int:pk>/moderation/', PropertyReviewModerationUpdate.as_view(), name='property-review-moderation'),
    path('<int:property_pk>/comments/', PropertyCommentList.as_view(), name='property-comment-list'),
    path('<int:property_pk>/comments/create/', PropertyCommentCreate.as_view(), name='property-comment-create'),
    path('comments/<int:pk>/moderation/', PropertyCommentModerationUpdate.as_view(), name='property-comment-moderation'),
    path('comments/<int:pk>/delete/', PropertyCommentDelete.as_view(), name='property-comment-delete'),
]
