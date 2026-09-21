from django.urls import path

from .views import ProfileCreate, ProfileList, ProfileDelete, ProfileUpdate

urlpatterns = [
    path('profile/', ProfileCreate.as_view(), name='profile'),
    path('profile/update/', ProfileUpdate.as_view(), name='update_profile'),
    path('profile/delete/', ProfileDelete.as_view(), name='delete_profile'),
    path('profile/view_details/', ProfileList.as_view(), name='view_details'),

]