from django.contrib import admin
from .models import ProductFeedback


@admin.register(ProductFeedback)
class ProductFeedbackAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "status", "severity", "profile", "created_at", "reviewed_by")
    list_filter = ("category", "status", "severity", "allow_public_idea", "created_at")
    search_fields = ("title", "description", "profile__username", "profile__email")
    readonly_fields = ("profile", "created_at", "updated_at", "reviewed_by", "reviewed_at")
