from django.contrib import admin
from .models import *

from django.contrib import admin
from .models import Expense
from .action import export_expenses_to_csv  # Import the custom action

class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'amount', 'currency', 'date')
    actions = [export_expenses_to_csv]  # Add the custom action

admin.site.register(Profile)
admin.site.register(Coordinate)
admin.site.register(Expense, ExpenseAdmin)