# users/models.py
from django.db import models
from django.contrib.auth.models import User # Import Django's built-in User model

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
    def __str__(self):
        # This will make it easier to identify profiles in the admin panel
        return f'{self.user.username} Profile'