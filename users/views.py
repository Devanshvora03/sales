from django.contrib.auth.views import LoginView, PasswordResetView, PasswordChangeView
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.urls import reverse_lazy
from django.contrib import messages
from django.views import View
from .models import * 
from .forms import *
import folium
import csv
from .utils import get_distance

def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

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
                currency = form.cleaned_data.get('currency'),
                modes=form.cleaned_data.get('modes'),
                rate=form.cleaned_data.get('rate'),
                total_km=form.cleaned_data.get('total_km'),
                remarks=form.cleaned_data.get('remarks'),
                image=request.POST.get('image'),
                user_id = request.user
                )
            new_expense.total_amount = float(new_expense.rate) * float(new_expense.total_km)
            new_expense.save()
            print(request.FILES)
            messages.success(request, 'Expense added successfully.')
            return redirect('/expense/')
    expenses = Expense.objects.filter(user_id=user)
    coordinates = Coordinate.objects.filter(user= request.user).order_by('date_time')
    head = True
    prev_name = ''
    prev_lat = 0
    prev_long = 0
    sum = 0
    e = []
    for c in coordinates:
        if head:
            prev_name = c.hospital
            prev_lat = c.latitude
            prev_long = c.longitude
            dist = 0 
            head = False
            e.append({'date': c.date_time, 'from': 'Home', 'to' : c.hospital.hospital_name, 'total': 0 ,'rate' : 0 , 'remarks' : c.product , 'distance':dist})
        else:
            dist = get_distance(prev_lat, prev_long, c.latitude, c.longitude)
            sum += dist
            prate = Profile.objects.get(user = request.user).rate
            rate = float( prate * dist)
            e.append({'date': c.date_time, 'from': prev_name, 'distance':dist,'to' : c.hospital.hospital_name, 'total': sum ,'rate' : rate , 'remarks' : c.product})
            prev_name = c.hospital
            prev_lat = c.latitude
            prev_long = c.longitude
    print(sum)
    for en in expenses:
        e.append({'date': en.date, 'from': 'None', 'to' : 'None', 'total': en.total_amount ,'rate' : en.total_amount , 'remarks' : en.remarks , 'distance':dist})
    e = e.sort(key=lambda x: x['date'])
    return render(request, 'users/expense.html',{'form':form, 'expenses':expenses , 'e':e})


def delete_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id)

    if expense.user_id == request.user:
        expense.delete()
        messages.warning(request, 'Expense deleted successfully.')
    else:
        messages.error(request, 'You do not have permission to delete this expense.')

    return redirect('expense')


def download_expenses_csv(request):
    coordinates = Coordinate.objects.filter(user_id=request.user).order_by('date_time')
    head = True
    prev_name = ''
    prev_lat = 0
    prev_long = 0  
    sum = 0
    for c in coordinates:  
        if head:
            prev_name = c.hospital
            prev_lat = c.latitude
            prev_long = c.longitude
            head = False
        else:
            dist = get_distance(prev_lat, prev_long, c.latitude, c.longitude)
            sum += dist
            prev_name = c.hospital
            prev_lat = c.latitude
            prev_long = c.longitude

        
    print(sum)     
            
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
        department = request.POST.get('department')
        hospital_id = request.POST.get('hospital_name')
        person = request.POST.get('person_name')
        department = request.POST.get('department')     
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        person_obj,_ = Person.objects.get_or_create(name = person , department = department)
        print(hospital_id , type(hospital_id))
        hospital_obj = Hospital.objects.get(id = int(hospital_id))
        product_obj = request.POST.get('product')
        outcome_obj = request.POST.get('outcome')
        new_Coordinate = Coordinate.objects.create(
            user_id = request.user,
            latitude = latitude,
            longitude = longitude,
            person_name = person_obj,
            hospital = hospital_obj,
            product = product_obj,
            outcome = outcome_obj
            )   
        new_Coordinate.save()
        messages.success(request, 'coordinate added successfully.')
        return JsonResponse({'message': 'Coordinate Updated successfully' , 'status' : 'success' ,'code' : 200  })

    hospitals = Hospital.objects.all()
    Coordinates = Coordinate.objects.filter(user_id=user)
    department = Person.objects.values_list('department', flat=True).distinct()
    return render(request, 'users/coordinate.html',{'form': form, 'coordinate' : Coordinates , 'hospitals' : hospitals , 'department' : department})

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
    

def get_person_hospital(request):
    if is_ajax:
        hospital_id = request.GET.get('hospital_id')
        hospital = Hospital.objects.get(id = hospital_id)
        persons = hospital.staff.all()  
        print(persons)  
        # persons = serialize('json', persons)
        content = ''
        for i in persons:
            content += '<option value="'+str(i.name)+'">'+str(i.name)+'</option>'
        return JsonResponse({'content': content})
        
    

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