import folium
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordChangeView
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.views import View
from django.contrib.auth.decorators import login_required
from .models import * 
from .forms import *

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
                amount = form.cleaned_data.get('amount'),
                currency = form.cleaned_data.get('currency'),
                amount_details = form.cleaned_data.get('amount_details'),
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
        messages.success(request, 'Expense deleted successfully.')
    else:
        messages.error(request, 'You do not have permission to delete this expense.')

    return redirect('expense')

def coordinate(request):
    return render(request, 'users/coordinate.html')

def update_coordinates(request):
    if request.method == 'POST':
        
        coordinates = Coordinate.objects.create(
            latitude = request.POST.get('latitude'),
            longitude = request.POST.get('longitude')
        )
        coordinates.save()
        print(coordinates.latitude, coordinates.longitude)
        return JsonResponse({'message': 'Coordinates updated successfully'})
    
# def map_view(request):
#     # Retrieve coordinates from the Coordinate model
#     coordinates = Coordinate.objects.filter(user_id=request.user).values('latitude', 'longitude', 'date_time')
#     return render(request, 'users/map.html', {'coordinates': list(coordinates)})

def maps(request):
    coordinates = Coordinate.objects.all()
    fp = coordinates.first()
    coordinate_list = []
    mapObject = folium.Map(location=[fp.latitude, fp.longitude])  # Specify latitude and longitude separately
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