# users/models.py
from django.db import models
from django.contrib.auth.models import User # Import Django's built-in User model
from django.utils import timezone
from datetime import timedelta
import random
import string

class PasswordResetOTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        # Set expiration time (e.g., 10 minutes from creation)
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=10)
        super().save(*args, **kwargs)

    def is_expired(self):
        return timezone.now() > self.expires_at

    @staticmethod
    def generate_otp(length=6):
        # Generate a random 6-digit OTP
        return ''.join(random.choices(string.digits, k=length))

    def __str__(self):
        return f"OTP for {self.user.username}"

# This new Profile model will store the extra information 
# that was in your old User model.
class Profile(models.Model):
    # This line creates a one-to-one link with Django's User model.
    # Each user will have exactly one profile.
    user = models.OneToOneField(User, on_delete=models.CASCADE) 
    
    # These are your custom fields
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    dietary_preference = models.CharField(max_length=100, blank=True, null=True, help_text="e.g., vegan")
    mobile_number = models.CharField(max_length=20, unique=True, null=True, blank=True, help_text="Include country code, e.g., +91XXXXXXXXXX")
    def __str__(self):
        # This will make it easier to identify profiles in the admin panel
        return f'{self.user.username} Profile'