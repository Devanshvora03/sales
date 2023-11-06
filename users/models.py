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
    amount = models.CharField(max_length=10)
    currency = models.CharField(max_length=10, default="INR")
    amount_details = models.TextField(blank=True, null=True,)
    date = models.DateField(auto_now_add=True, blank=True, null=True,)

    def __str__(self):
        return self.user_id.username + "'s expense at " + str(self.date)
    
class Coordinate(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    date_time = models.DateTimeField(blank=True, null=True, auto_now_add=True)

    def __str__(self):
        return 'Coordinates at  ' + str(self.date_time)