from django.urls import path
from .views import *

urlpatterns = [
    path('', home, name='users-home'),
    path('register/', RegisterView.as_view(), name='users-register'),
    path('profile/', profile, name='users-profile'),
    path('expense/', expense, name='expense'),
    path('coordinate/', coordinate, name='coordinate'),
    path('update-coordinates/', update_coordinates, name='update-coordinates'),
]