from django.contrib.auth.models import User
from django.db import models

# Extending User Model Using a One-To-One Link
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField()
    phone = models.CharField(max_length = 12, blank=True, null=True)
    address = models.CharField(max_length = 100, blank=True, null=True)
    
    def __str__(self):
        return self.user.username


class Expense(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    km=models.IntegerField(null=True,)
    modes = models.CharField(max_length=20,null=True,)
    rate = models.CharField(max_length=10,null=True, default = 3.5,)
    total_amount=models.IntegerField(null=True)
    total_km=models.IntegerField(null=True,)
    remarks=models.CharField(max_length=50,null=True,)
    date = models.DateField(auto_now_add=True, blank=True, null=True,)

    def __str__(self):
        return self.user_id.username + "'s expense at " + str(self.date)
    

class Person(models.Model):
    name = models.CharField(max_length=25, null=True)
    dept = models.CharField(max_length=20, null=True)

    def __str__(self):
            return self.name


class Hospital(models.Model):
    hospital_name = models.CharField(max_length=50, null=True)
    hospital_address = models.CharField(max_length=150, null=True)
    
    def __str__(self):
        return self.name
    

class Coordinate(models.Model):
    CHOICES= [
    ('Biomedical', 'Biomedical'),
    ('Neuro', 'Neuro'),
    ('ICU', 'ICU'),
    ('cathlab', 'cathlab'),
    ('Management', 'Management'),
    ('purchase', 'purchase')
    ]
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    hospital_name = models.CharField(max_length=50)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    date_time = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    hospital_address=models.CharField(max_length=50,null=True)
    department = models.CharField(max_length=10,choices=CHOICES)
    product  = models.CharField(max_length=50, null=True)
    outcome = models.CharField(max_length=50, null=True)

    def __str__(self):
        return 'Coordinates of' + str(self.user_id) + 'at' + str(self.date_time)


class ManagerProfile(models.Model):
    user_id = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    company_name = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.user_id.username


class EmployeeManager(models.Model):
    employee = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True, verbose_name='Employee', related_name='employee')
    manager = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, verbose_name='Manager', related_name='manager')