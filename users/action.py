from django.http import HttpResponse
import csv

def export_expenses_to_csv(modeladmin, request, queryset):
    # Define the filename for the CSV file
    filename = "expenses.csv"

    # Create an HTTP response with CSV content type and attachment header
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    # Create a CSV writer
    csv_writer = csv.writer(response)
    
    # Write the header row with column names
    header = ["User", "Amount", "Currency", "Amount Details", "Date"]
    csv_writer.writerow(header)

    # Write the data rows
    for expense in queryset:
        data_row = [
            expense.user_id.username,
            expense.amount,
            expense.currency,
            expense.amount_details,
            expense.date
        ]
        csv_writer.writerow(data_row)

    return response

export_expenses_to_csv.short_description = "Export selected expenses to CSV"