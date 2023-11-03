from django.db import models
from django.contrib.auth.models import User
from PIL import Image


# Extending User Model Using a One-To-One Link
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(default='default.jpg', upload_to='profile_images', blank=True)
    bio = models.TextField()
    phone = models.CharField(max_length = 12, blank=True, null=True)
    address = models.CharField(max_length = 100, blank=True, null=True)

    def __str__(self):
        return self.user.username

class Expense(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.CharField(max_length=10)
    currency = models.CharField(max_length=10, default="INR")
    amount_details = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user_id.username

