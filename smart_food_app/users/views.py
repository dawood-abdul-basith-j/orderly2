# users/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm, SetPasswordForm
from django.contrib import messages
from .forms import SignUpForm, ProfileUpdateForm
from .models import Profile, PasswordResetOTP
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta # Make sure timedelta is imported

# --- Authentication Views ---

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save() # Saves User model
            mobile = form.cleaned_data.get('mobile_number')
            address_data = form.cleaned_data.get('address') # Get address data
            profile, created = Profile.objects.get_or_create(user=user)
            profile.mobile_number = mobile
            profile.address = address_data # Save address
            profile.save()
            login(request, user)
            messages.success(request, "Registration successful.")
            return redirect('menu_home')
    else:
        form = SignUpForm()
    return render(request, 'users/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login_identifier = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = None
            try:
                profile = Profile.objects.select_related('user').get(mobile_number=login_identifier)
                user_to_auth = profile.user
                user = authenticate(username=user_to_auth.username, password=password)
            except Profile.DoesNotExist:
                user = authenticate(username=login_identifier, password=password)
            
            if user is not None:
                login(request, user)
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                else:
                    messages.success(request, f"Welcome back, {user.username}!")
                    return redirect('menu_home')
            else:
                messages.error(request,"Invalid username/mobile or password.")
        else:
             messages.error(request,"Invalid username/mobile or password.")
    form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect('menu_home')

# --- Profile and Settings Views ---

@login_required
def profile_view(request):
    user_orders = Order.objects.filter(user=request.user).exclude(status='Pending').order_by('-order_time')
    context = {
        'user_orders': user_orders
    }
    return render(request, 'users/profile.html', context)

@login_required
def settings_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your settings have been updated successfully!')
            return redirect('settings')
    else:
        form = ProfileUpdateForm(instance=profile)
    context = {'form': form}
    return render(request, 'users/settings.html', context)

# --- OTP Password Reset Views ---

def request_password_reset_otp(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        
        # --- FIX 1: Use filter().first() to avoid MultipleObjectsReturned ---
        user = User.objects.filter(email=email).first()

        if user: # Check if a user was found
            PasswordResetOTP.objects.filter(user=user).delete()
            otp_code = PasswordResetOTP.generate_otp()
            otp_instance = PasswordResetOTP.objects.create(user=user, otp=otp_code)

            subject = 'Your Password Reset OTP for Orderly'
            message = f'Hi {user.username},\n\nYour OTP is: {otp_code}\n\nExpires in 10 minutes.\n\nIgnore if not requested.'
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [user.email]
            try:
                send_mail(subject, message, from_email, recipient_list)
                request.session['reset_email'] = user.email
                messages.success(request, 'OTP sent to your email (check console).')
                return redirect('verify_reset_otp')
            except Exception as e:
                 messages.error(request, f'Failed to send email: {e}')
        else:
            messages.error(request, 'No user found with that email address.')

    return render(request, 'users/request_otp.html')


def verify_password_reset_otp(request):
    email = request.session.get('reset_email')
    if not email:
        messages.error(request, 'Session expired. Please request OTP again.')
        return redirect('request_otp')
        
    try:
        # --- FIX 2: Use filter().first() here as well ---
        user = User.objects.filter(email=email).first()
        if not user: # Handle case where user might have been deleted
             raise User.DoesNotExist
        # --- END FIX ---
    except User.DoesNotExist:
         messages.error(request, 'User error. Please request OTP again.')
         return redirect('request_otp')

    if request.method == 'POST':
        otp_entered = request.POST.get('otp')
        try:
            # We can still use .get() here because user is specific
            otp_instance = PasswordResetOTP.objects.get(user=user, otp=otp_entered)
            if otp_instance.is_expired():
                messages.error(request, 'OTP expired. Please request a new one.')
                otp_instance.delete()
                return redirect('request_otp')
            else:
                request.session['reset_user_id'] = user.id
                otp_instance.delete()
                if 'reset_email' in request.session: del request.session['reset_email']
                messages.success(request, 'OTP verified. Set your new password.')
                return redirect('set_new_password')
        except PasswordResetOTP.DoesNotExist:
            messages.error(request, 'Invalid OTP entered.')

    return render(request, 'users/verify_otp.html', {'email': email})


def set_new_password(request):
    user_id = request.session.get('reset_user_id')
    if not user_id:
        messages.error(request, 'Session invalid. Start reset process again.')
        return redirect('request_otp')
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, 'User error. Start reset process again.')
        return redirect('request_otp')

    if request.method == 'POST':
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            if 'reset_user_id' in request.session: del request.session['reset_user_id']
            messages.success(request, 'Password successfully reset! You can log in.')
            return redirect('login')
    else:
        form = SetPasswordForm(user)
    return render(request, 'users/set_new_password.html', {'form': form})