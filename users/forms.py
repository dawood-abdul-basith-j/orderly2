# users/forms.py
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile # Import Profile model
from django.db import transaction # Import transaction
import logging

logger = logging.getLogger(__name__)

# --- RECTIFIED SIGNUP FORM ---
class SignUpForm(UserCreationForm):
    # Add the fields that are not in the default UserCreationForm
    email = forms.EmailField(max_length=254, required=True, help_text='Required. Inform a valid email address.')
    mobile_number = forms.CharField(max_length=20, required=True, help_text='Enter mobile number with country code, e.g., +91XXXXXXXXXX')
    first_name = forms.CharField(max_length=150, required=False)
    last_name = forms.CharField(max_length=150, required=False)
    
    class Meta(UserCreationForm.Meta):
        """
        Inherit from the base Meta class to get its fields
        (which handles username and password logic)
        """
        model = User
        # Add your new fields to the default fields
        fields = UserCreationForm.Meta.fields + ('email', 'first_name', 'last_name',)

    @transaction.atomic # Use a transaction to ensure user and profile save together
    def save(self, commit=True):
        """
        Override save to handle the extra fields.
        """
        user = super().save(commit=False)
        user.email = self.cleaned_data.get('email')
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')
        mobile = self.cleaned_data.get('mobile_number')
        
        def save_profile():
            try:
                profile, created = Profile.objects.get_or_create(user=user)
                profile.mobile_number = mobile
                profile.phone = mobile
                profile.save()
            except Exception as e:
                logger.error(f"Could not save mobile number for user {user.username}. Error: {e}")

        if commit:
            user.save()
            save_profile()
        else:
            old_save_m2m = getattr(self, 'save_m2m', None)
            def save_m2m():
                if old_save_m2m:
                    old_save_m2m()
                save_profile()
            self.save_m2m = save_m2m
            
        return user

# --- ProfileUpdateForm ---
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['phone', 'address', 'dietary_preference']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
            'dietary_preference': forms.TextInput(attrs={'placeholder': 'e.g., vegan, gluten_free'})
        }
        help_texts = {
            'dietary_preference': 'Enter comma-separated tags (e.g., vegetarian, nut_allergy)',
        }

    def save(self, commit=True):
        profile = super().save(commit=False)
        if profile.phone:
            profile.mobile_number = profile.phone
        if commit:
            profile.save()
        return profile