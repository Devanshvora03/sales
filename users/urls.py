from django.urls import path
from .views import *

urlpatterns = [
    path('', home, name='users-home'),
    path('register/', RegisterView.as_view(), name='users-register'),
    path('profile/', profile, name='users-profile'),
    path('expense/', expense, name='expense'),
    path('coordinate/', coordinate, name='coordinate'),
    path('update-coordinates/', update_coordinates, name='update-coordinates'),
    path('expense/delete/<int:expense_id>/', delete_expense, name='delete-expense'),
    path('download-expenses-csv/', download_expenses_csv, name='download-expenses-csv'),
    path('maps/', maps, name='maps'),
    path('get_person/', get_person_hospital, name='get_person'),
]