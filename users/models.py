from django.contrib.auth.models import User
from django.db import models

# Extending User Model Using a One-To-One Link
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField()
    phone = models.CharField(max_length = 12, blank=True, null=True)
    address = models.CharField(max_length = 100, blank=True, null=True)
    rate = models.FloatField(null=True , blank=True)
    
    def __str__(self):
        return self.user.username


class Expense(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    currency = models.CharField(max_length=10, default="INR")
    modes = models.CharField(max_length=20,null=True,)
    total_amount =models.IntegerField(null=True,)
    rate = models.CharField(max_length=10,null=True, default = 3.5)
    total_km=models.IntegerField(null=True,)
    remarks=models.CharField(max_length=50,null=True,)
    date = models.DateField(auto_now_add=True, blank=True, null=True,)
    image = models.ImageField(upload_to='Expenses', blank=True, null=True)

    def __str__(self):
        return self.user_id.username + "'s expense at " + str(self.date)
    

class Person(models.Model):
    CHOICES= [
    ('Biomedical', 'Biomedical'),
    ('Neuro', 'Neuro'),
    ('Management', 'Management'),
    ('Purchase', 'Purchase'),
    ('Arterial Bloog Gas Analysis', 'Arterial Bloog Gas Analysis'),
    ('Emergency Testing', 'Emergency Testing'),
    ('Semen Analysis', 'Semen Analysis'),
    ('HbA1C Testing', 'HbA1C Testing'),
    ('Neuro Surgicals', 'Neuro Surgicals'),
    ('Surgical Microscopy', 'Surgical Microscopy'),
    ('Autoimmune Testing', 'Autoimmune Testing'),
    ]
    name = models.CharField(max_length=25, null=True)
    rate = models.FloatField(null=True , blank=True)
    
    department = models.CharField(max_length=50,choices=CHOICES, blank=True, null=True)

    def __str__(self):
            return self.name


class Hospital(models.Model):
    hospital_name = models.CharField(max_length=50, null=True)
    hospital_address = models.CharField(max_length=150, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    staff = models.ManyToManyField(Person)

    def __str__(self):
        return self.hospital_name
    

class Coordinate(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    date_time = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    
    person_name =  models.ForeignKey(Person, on_delete=models.CASCADE, blank=True, null=True)
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, blank=True, null=True)
    
    product  = models.TextField(blank=True, null=True)
    outcome = models.TextField(blank=True, null=True)

    def __str__(self):
        return 'Coordinates of ' + str(self.user_id) + 'at' + str(self.date_time)


class ManagerProfile(models.Model):
    user_id = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    company_name = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.user_id.username


class EmployeeManager(models.Model):
    employee = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True, verbose_name='Employee', related_name='employee')
    manager = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, verbose_name='Manager', related_name='manager')