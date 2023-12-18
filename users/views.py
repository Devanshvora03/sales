from django.contrib.auth.views import LoginView, PasswordResetView, PasswordChangeView
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from datetime import datetime, timedelta
from django.urls import reverse_lazy
from django.contrib import messages
from django.views import View
from .models import * 
from .forms import *
import folium
import csv
from django.db.models import Q  # Import Q for complex queries
from django.utils import timezone  # Import timezone


def home(request):
    return render(request, 'users/home.html')


class RegisterView(View):
    form_class = RegisterForm
    initial = {'key': 'value'}
    template_name = 'users/register.html'

    def dispatch(self, request, *args, **kwargs):
        # will redirect to the home page if a user tries to access the register page while logged in
        if request.user.is_authenticated:
            return redirect(to='/')

        # else process dispatch as it otherwise normally would
        return super(RegisterView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)

        if form.is_valid():
            form.save()

            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}')

            return redirect(to='login')

        return render(request, self.template_name, {'form': form})


# Class based view that extends from the built in login view to add a remember me functionality
class CustomLoginView(LoginView):
    form_class = LoginForm

    def form_valid(self, form):
        remember_me = form.cleaned_data.get('remember_me')

        if not remember_me:
            # set session expiry to 0 seconds. So it will automatically close the session after the browser is closed.
            self.request.session.set_expiry(0)

            # Set session as modified to force data updates/cookie to be saved.
            self.request.session.modified = True

        # else browser session will be as long as the session cookie time "SESSION_COOKIE_AGE" defined in settings.py
        return super(CustomLoginView, self).form_valid(form)
    

class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = 'users/password_reset.html'
    email_template_name = 'users/password_reset_email.html'
    subject_template_name = 'users/password_reset_subject'
    success_message = "We've emailed you instructions for setting your password, " \
                      "if an account exists with the email you entered. You should receive them shortly." \
                      " If you don't receive an email, " \
                      "please make sure you've entered the address you registered with, and check your spam folder."
    success_url = reverse_lazy('users-home')


class ChangePasswordView(SuccessMessageMixin, PasswordChangeView):
    template_name = 'users/change_password.html'
    success_message = "Successfully Changed Your Password"
    success_url = reverse_lazy('users-home')


@login_required
def profile(request):
    if request.method == 'POST':
        user_form = UpdateUserForm(request.POST, instance=request.user)
        profile_instance = Profile.objects.get(user=request.user)
        profile_form = UpdateProfileForm(request.POST, request.FILES, instance=profile_instance)

        if user_form.is_valid() and profile_form.is_valid():
            print(user_form , '=== user form ===')
            print(profile_form , '=== profile form ===')
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile is updated successfully')
            return redirect(to='users-profile')
        elif user_form.is_valid():
            print(user_form , " === user form === ")
        elif profile_form.is_valid():
            print(profile_form , "=== profile form ===")
    else:
        user_form = UpdateUserForm(instance=request.user)
        profile_instance = Profile.objects.get(user=request.user)
        print ('=== Profile Instance ===' , profile_instance.phone )
        print ('=== User Instance ===' , request.user)
        profile_form = UpdateProfileForm(instance=profile_instance)

    return render(request, 'users/profile.html', {'user_form': user_form, 'profile_form': profile_form})


def expense(request):
    user = request.user
    form = ExpenseForm()
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            new_expense = Expense.objects.create(

                modes=form.cleaned_data.get('Modes'),
                km=form.cleaned_data.get('Kilometers'),
                rate=form.cleaned_data.get('Rates'),
                total_km=form.cleaned_data.get('Total Kilometer'),
                remarks=form.cleaned_data.get('Amount Details'),
                total_amount=form.cleaned_data.get('Amount'),

                user_id = request.user
                )
            new_expense.save()
            messages.success(request, 'Expense added successfully.')
            return redirect('/expense/')
    expenses = Expense.objects.filter(user_id=user)
    return render(request, 'users/expense.html',{'form':form, 'expenses':expenses})


def delete_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id)

    if expense.user_id == request.user:
        expense.delete()
        messages.warning(request, 'Expense deleted successfully.')
    else:
        messages.error(request, 'You do not have permission to delete this expense.')

    return redirect('expense')


def download_expenses_csv(request):
    expenses = Expense.objects.filter(user_id=request.user)

    # Create an HTTP response with CSV content type and attachment header
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="expenses.csv"'

    csv_writer = csv.writer(response)

    # Write the header row with column names
    header = ['Sr.no.', 'Date', 'User', 'Mode', 'Rate', 'Total Distance', 'Currency', 'Total Amount', 'Amount Details']
    csv_writer.writerow(header)

    # Write the data rows
    counter = 0
    for expense in expenses:
        # Format the date as a string in the desired format (e.g., 'YYYY-MM-DD')
        formatted_date = expense.date.strftime('%Y-%m-%d')

        # Increment the counter for each expense
        counter += 1

        data_row = [
            counter,
            formatted_date,
            expense.user_id.username,
            expense.modes,
            expense.rate,
            expense.total_km,
            expense.currency, 
            expense.total_amount,
            expense.remarks,
        ]
        csv_writer.writerow(data_row)

        if counter >= 10:
            break

    return response


def coordinate(request):
    user = request.user
    form = CoordinateForm()
    if request.method == 'POST':
        form = CoordinateForm(request.POST)
        if form.is_valid():
            new_Coordinate = Coordinate.objects.create(
                hospital_name = form.cleaned_data.get('hospital_name'),
                hospital_address=form.cleaned_data.get('hospital_address'),
                department=form.cleaned_data.get('department'),
                user_id = request.user
                )
            new_Coordinate.save()
            messages.success(request, 'coordinate added successfully.')
            return redirect('/coordinate/')
    Coordinates = Coordinate.objects.filter(user_id=user)
    return render(request, 'users/coordinate.html',{'form': form, 'coordinate' : Coordinates})

@login_required(login_url='/login/')
def update_coordinates(request):

    if request.method == 'POST':
        coordinates = Coordinate.objects.create(
            latitude=request.POST.get('latitude'),
            longitude=request.POST.get('longitude'),
            user_id = request.user
        )
        coordinates.save()
        print(coordinates.latitude, coordinates.longitude)
        return JsonResponse({'message': 'Coordinates updated successfully'})
    

def maps(request):
    if request.method == 'POST':
        start = request.POST.get('start')
        end = request.POST.get('end')
        coordinates = Coordinate.objects.filter(user_id= request.user)
        coordinate = coordinate.filter(date_time__range=(start, end)) 
        fp = coordinates.first()
        coordinate_list = []
        mapObject = folium.Map(location=[fp.latitude, fp.longitude])
        for i in coordinates:
            #print(i.latitude, i.longitude)
            coordinate_list.append((i.latitude, i.longitude))
            folium.Marker(location=[i.latitude, i.longitude]).add_to(mapObject)
            folium.PolyLine(coordinate_list, color="red", weight=2.5, opacity=1).add_to(mapObject)
        folium.LayerControl().add_to(mapObject)
        mapContext = mapObject._repr_html_()
        context = {
            'maps': mapContext,
        }
        return JsonResponse({'message': 'Coordinates updated successfully' , 'context': context})   
    
    coordinates = Coordinate.objects.filter(user_id= request.user)
    fp = coordinates.first()
    coordinate_list = []
    mapObject = folium.Map(location=[fp.latitude, fp.longitude])
    for i in coordinates:
        #print(i.latitude, i.longitude)
        coordinate_list.append((i.latitude, i.longitude))
        folium.Marker(location=[i.latitude, i.longitude]).add_to(mapObject)
        folium.PolyLine(coordinate_list, color="red", weight=2.5, opacity=1).add_to(mapObject)
    folium.LayerControl().add_to(mapObject)
    mapContext = mapObject._repr_html_()
    context = {
        'maps': mapContext,
    }
    return render(request, 'users/maps.html', context)