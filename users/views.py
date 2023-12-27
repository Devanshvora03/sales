from django.contrib.auth.views import LoginView, PasswordResetView, PasswordChangeView
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.urls import reverse_lazy
from django.contrib import messages
from .utils import get_distance
from django.views import View
from datetime import datetime
from .models import *
from .forms import *
import folium
import pytz
import csv


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


def home(request):
    return render(request, 'users/home.html')


class RegisterView(View):
    form_class = RegisterForm
    initial = {'key': 'value'}
    template_name = 'users/register.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(to='/')

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


class CustomLoginView(LoginView):
    form_class = LoginForm

    def form_valid(self, form):
        remember_me = form.cleaned_data.get('remember_me')

        if not remember_me:
            self.request.session.set_expiry(0)
            self.request.session.modified = True

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
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile is updated successfully')
            return redirect(to='users-profile')
        elif user_form.is_valid():
            user_form.save()
        elif profile_form.is_valid():
            profile_form.save()
    else:
        user_obj = User.objects.get(username=request.user.username)
        profile_instance = Profile.objects.get(user=user_obj)
        user_form = UpdateUserForm(instance=user_obj)
        profile_form = UpdateProfileForm(instance=profile_instance)

    return render(request, 'users/profile.html', {'user_form': user_form, 'profile_form': profile_form})


def expense(request):
    user = request.user
    form = ExpenseForm()
    if request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES)
        print(form.is_valid())
        # if form.is_valid():
        #     # user_id = request.user
        #     print(request.FILES['image'])
        #     obj = form.save()
        #     print(obj)
        #     messages.success(request, 'Expense added successfully.')
        #     return redirect('/expense/')
        
        if form.is_valid():
            expense_instance = form.save(commit=False)
            expense_instance.user_id = user
            expense_instance.total_km = 0
            expense_instance.save()
            messages.success(request, 'Expense added successfully.')
            return redirect('/expense/')

    expenses = Expense.objects.filter(user_id=user)
    coordinates = Coordinate.objects.filter(user_id=request.user).order_by('date_time')
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
            distance = 0
            head = False
            obj = {'date': c.date_time, 'from': 'Home', 'to': c.hospital.hospital_name, 'total': 0, 'rate': 0,
                   'remarks': c.product, 'distance': distance, 'type': 'location', 'id': c.id}
            e.append(obj)
        else:
            distance = get_distance(prev_lat, prev_long, c.latitude, c.longitude)
            sum += distance
            prate = Profile.objects.get(user=request.user).rate or 3.5
            rate = float(prate * distance)
            obj = {'date': c.date_time, 'from': prev_name, 'distance': distance, 'to': c.hospital.hospital_name,
                   'total': rate, 'rate': prate, 'remarks': c.product, 'type': 'location', 'id': c.id}
            e.append(obj)
            prev_name = c.hospital
            prev_lat = c.latitude
            prev_long = c.longitude

    for en in expenses:
        e.append({'date': datetime.combine(en.date, datetime.min.time()).replace(tzinfo=pytz.UTC), 'from': 'None',
                  'to': 'None', 'total': en.total_amount, 'rate': 0, 'remarks': en.remarks, 'distance': distance,
                  'type': 'expense', 'id': en.id})

    e.sort(key=lambda x: x['date'])

    return render(request, 'users/expense.html', context={'form': form, 'ex': e})


def delete_expense(request, expense_id):
    a = get_object_or_404(Expense, id=expense_id)

    if a.user_id == request.user:
        a.delete()
        messages.warning(request, 'Expense deleted successfully.')
    else:
        messages.error(request, 'You do not have permission to delete this expense.')

    return redirect('expense')


def download_expenses_csv(request):

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="expenses.csv"'

    csv_writer = csv.writer(response)
    header = ['Sr.no.', 'Date', 'User', 'Rate', 'Total Distance', 'From', 'To', 'Total Amount', 'Remarks']
    csv_writer.writerow(header)
    user=request.user
    expenses = Expense.objects.filter(user_id=user)
    coordinates = Coordinate.objects.filter(user_id=request.user).order_by('date_time')
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
            distance = 0
            head = False
            obj = {'date': c.date_time, 'from': 'Home', 'to': c.hospital.hospital_name, 'total': 0, 'rate': 0,
                   'remarks': c.product, 'distance': distance, 'type': 'location', 'id': c.id}
            e.append(obj)

        else:
            distance = get_distance(prev_lat, prev_long, c.latitude, c.longitude)
            sum += distance
            prate = Profile.objects.get(user=request.user).rate or 3.5
            rate = float(prate * distance)
            obj = {'date': c.date_time, 'from': prev_name, 'distance': distance, 'to': c.hospital.hospital_name,
                   'total': rate, 'rate': prate, 'remarks': c.product, 'type': 'location', 'id': c.id}
            e.append(obj)
            prev_name = c.hospital
            prev_lat = c.latitude
            prev_long = c.longitude

    for en in expenses:
        e.append({'date': datetime.combine(en.date, datetime.min.time()).replace(tzinfo=pytz.UTC), 'from': 'None',
                  'to': 'None', 'total': en.total_amount, 'rate': 0, 'remarks': en.remarks, 'distance': distance,
                  'type': 'expense', 'id': en.id})

    e.sort(key=lambda x: x['date'])
    counter = 0

    for expense in e:
        formatted_date = expense['date'].strftime('%Y-%m-%d')
        counter += 1
        data_row = [
            counter,
            formatted_date,
            user.username,
            expense['rate'],
            expense['distance'],
            expense['from'],
            expense['to'],
            expense['total'],
            expense['remarks'],
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
        person_obj, _ = Person.objects.get_or_create(name=person, department=department)
        hospital_obj = Hospital.objects.get(id=int(hospital_id))
        product_obj = request.POST.get('product')
        outcome_obj = request.POST.get('outcome')
        new_Coordinate = Coordinate.objects.create(
            user_id=request.user,
            latitude=latitude,
            longitude=longitude,
            person_name=person_obj,
            hospital=hospital_obj,
            product=product_obj,
            outcome=outcome_obj
        )
        new_Coordinate.save()
        messages.success(request, 'coordinate added successfully.')
        return JsonResponse({'message': 'Coordinate Updated successfully', 'status': 'success', 'code': 200})

    hospitals = Hospital.objects.all()
    Coordinates = Coordinate.objects.filter(user_id=user)
    department = Person.objects.values_list('department', flat=True).distinct()
    return render(request, 'users/coordinate.html',
                  {'form': form, 'coordinate': Coordinates, 'hospitals': hospitals, 'department': department})


@login_required(login_url='/login/')
def update_coordinates(request):

    if request.method == 'POST':
        coordinates = Coordinate.objects.create(
            latitude=request.POST.get('latitude'),
            longitude=request.POST.get('longitude'),
            user_id=request.user
        )
        coordinates.save()
        return JsonResponse({'message': 'Coordinates updated successfully'})


def get_person_hospital(request):
    if is_ajax:
        hospital_id = request.GET.get('hospital_id')
        hospital = Hospital.objects.get(id=hospital_id)
        persons = hospital.staff.all()
        content = ''
        for i in persons:
            content += '<option value="' + str(i.name) + '">' + str(i.name) + '</option>'
        return JsonResponse({'content': content})


# def maps(request):
#     if request.method == 'POST':
#         start = request.POST.get('start')
#         end = request.POST.get('end')
#         coordinates = Coordinate.objects.filter(user_id=request.user)
#         coordinate = coordinate.filter(date_time__range=(start, end))
#         fp = coordinates.first()
#         coordinate_list = []
#         mapObject = folium.Map(location=[fp.latitude, fp.longitude])
#         for i in coordinates:
#             coordinate_list.append((i.latitude, i.longitude))
#             folium.Marker(location=[i.latitude, i.longitude]).add_to(mapObject)
#             folium.PolyLine(coordinate_list, color="red", weight=2.5, opacity=1).add_to(mapObject)
#         folium.LayerControl().add_to(mapObject)
#         mapContext = mapObject._repr_html_()
#         context = {
#             'maps': mapContext,
#         }
#         return JsonResponse({'message': 'Coordinates updated successfully', 'context': context})

#     coordinates = Coordinate.objects.filter(user_id=request.user)
#     fp = coordinates.first()
#     coordinate_list = []
#     mapObject = folium.Map(location=[fp.latitude, fp.longitude])
#     for i in coordinates:
#         coordinate_list.append((i.latitude, i.longitude))
#         folium.Marker(location=[i.latitude, i.longitude]).add_to(mapObject)
#         folium.PolyLine(coordinate_list, color="red", weight=2.5, opacity=1).add_to(mapObject)
#     folium.LayerControl().add_to(mapObject)
#     mapContext = mapObject._repr_html_()
#     context = {
#         'maps': mapContext,
#     }
#     return render(request, 'users/maps.html', context)


def maps(request):
    coordinates = Coordinate.objects.filter(user_id=request.user)

    if request.method == 'POST':
        start = request.POST.get('start')
        end = request.POST.get('end')
        coordinates = coordinates.filter(date_time__range=(start, end))

    if not coordinates.exists(): 
        mapObject = folium.Map(location=[20.5937, 78.9629], zoom_start=4)
    else:
        fp = coordinates.first()
        coordinate_list = []
        mapObject = folium.Map(location=[fp.latitude, fp.longitude])
        for i in coordinates:
            coordinate_list.append((i.latitude, i.longitude))
            folium.Marker(location=[i.latitude, i.longitude]).add_to(mapObject)
            folium.PolyLine(coordinate_list, color="red", weight=2.5, opacity=1).add_to(mapObject)
            
    folium.LayerControl().add_to(mapObject)
    mapContext = mapObject._repr_html_()
    context = {
        'maps': mapContext,
    }

    if request.method == 'POST':
        return JsonResponse({'message': 'Coordinates updated successfully', 'context': context})
    else:
        return render(request, 'users/maps.html', context)