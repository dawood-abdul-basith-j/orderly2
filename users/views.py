# users/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm, SetPasswordForm # Import SetPasswordForm
from django.contrib import messages
from orders.models import Order
from .forms import SignUpForm, ProfileUpdateForm # Import ProfileUpdateForm
from .models import Profile, PasswordResetOTP # Import Profile and PasswordResetOTP
from django.contrib.auth.decorators import login_required # Import login_required
from django.contrib.auth.models import User # Ensure User is imported
from django.core.mail import send_mail # For sending email
from django.conf import settings # To get default email sender
from django.utils import timezone
from django.db.models import Q
import ssl
import certifi
import logging

logger = logging.getLogger(__name__)

# --- Existing Authentication Views ---

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()  # Save user and profile with mobile number
            
            # Log the user in immediately
            login(request, user)
            messages.success(request, "Registration successful!")
            return redirect('menu_home')
        # Form is invalid, it will re-render with errors below
    else:
        form = SignUpForm()
    return render(request, 'users/signup.html', {'form': form})



def login_view(request):
    if request.method == 'POST':
        login_identifier = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        
        # If the identifier is a mobile number, resolve to the associated user's username
        username_to_auth = login_identifier
        try:
            profile = Profile.objects.select_related('user').filter(
                Q(mobile_number=login_identifier) | Q(phone=login_identifier)
            ).first()
            if profile:
                username_to_auth = profile.user.username
        except Exception:
            pass

        user = authenticate(request, username=username_to_auth, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            else:
                messages.success(request, f"Welcome back, {user.username}!")
                return redirect('menu_home')
        else:
            messages.error(request, "Invalid username/mobile or password.")
            form = AuthenticationForm(request)
            return render(request, 'users/login.html', {'form': form})

    form = AuthenticationForm(request)
    return render(request, 'users/login.html', {'form': form})


@login_required # Logout should require login
def logout_view(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect('menu_home')


@login_required
def profile_view(request):
    # Fetch all orders for this user, excluding the 'Pending' cart
    # Order by most recent first
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
            return redirect('settings') # Redirect back to settings page
    else:
        form = ProfileUpdateForm(instance=profile)
    context = {'form': form}
    return render(request, 'users/settings.html', context)

# --- Helper for sending OTP email ---

def send_otp_email(user, otp_code):
    """
    Sends an OTP email using Django's configured EMAIL_BACKEND,
    with fallback to unverified SSL SMTP in environments with custom CAs/MITM,
    or gracefully reporting the error.
    """
    subject = 'Your Password Reset OTP for Orderly'
    message = f'''Hi {user.username},

Your password reset OTP is: {otp_code}

This code will expire in 10 minutes.

If you did not request this reset, please ignore this email.

Best regards,
Orderly Team'''

    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None) or getattr(settings, 'EMAIL_HOST_USER', None)

    # Attempt 1: Standard Django send_mail
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=[user.email],
            fail_silently=False,
        )
        return True, None
    except Exception as e:
        logger.warning(f"Standard send_mail failed ({e}), attempting fallback STARTTLS with unverified context...")

    # Attempt 2: Direct SMTP with unverified context (handles self-signed/proxy interceptors)
    try:
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        import smtplib

        mime_msg = MIMEMultipart()
        mime_msg['From'] = from_email or settings.EMAIL_HOST_USER
        mime_msg['To'] = user.email
        mime_msg['Subject'] = subject
        mime_msg.attach(MIMEText(message, 'plain'))

        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT, timeout=10) as smtp:
            smtp.ehlo()
            smtp.starttls(context=context)
            smtp.ehlo()
            smtp.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            smtp.sendmail(settings.EMAIL_HOST_USER, [user.email], mime_msg.as_string())
        return True, None
    except Exception as e:
        logger.warning(f"Fallback SMTP failed: {e}")
        return False, str(e)


# --- New Views for OTP Password Reset ---

def request_password_reset_otp(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            PasswordResetOTP.objects.filter(user=user).delete() # Delete old OTPs
            otp_code = PasswordResetOTP.generate_otp()
            otp_instance = PasswordResetOTP.objects.create(user=user, otp=otp_code)

            email_sent, err_msg = send_otp_email(user, otp_code)
            request.session['reset_email'] = user.email

            if email_sent:
                messages.success(request, 'OTP has been sent to your email.')
                return redirect('verify_reset_otp')
            elif getattr(settings, 'DEBUG', False):
                # In development mode, display OTP so the developer/user isn't blocked by network/firewall issues
                messages.info(request, f"Development Mode: Your OTP is {otp_code} (email delivery failed: {err_msg})")
                return redirect('verify_reset_otp')
            else:
                PasswordResetOTP.objects.filter(user=user).delete()
                messages.error(request, 'Failed to send email. Please check your email settings or try again later.')
        except User.DoesNotExist:
            messages.error(request, 'No user found with that email address.')
        except Exception as e:
            messages.error(request, f'An unexpected error occurred: {e}')
    return render(request, 'users/request_otp.html')


def verify_password_reset_otp(request):
    email = request.session.get('reset_email')
    if not email:
        messages.error(request, 'Session expired. Please request OTP again.')
        return redirect('request_otp')
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
         messages.error(request, 'User error. Please request OTP again.')
         return redirect('request_otp')

    if request.method == 'POST':
        otp_entered = request.POST.get('otp')
        try:
            otp_instance = PasswordResetOTP.objects.get(user=user, otp=otp_entered)
            if otp_instance.is_expired():
                messages.error(request, 'OTP expired. Please request a new one.')
                otp_instance.delete()
                return redirect('request_otp')
            else:
                # Valid OTP
                request.session['reset_user_id'] = user.id # Store user ID for password set
                otp_instance.delete()
                if 'reset_email' in request.session: del request.session['reset_email']
                messages.success(request, 'OTP verified. Set your new password.')
                return redirect('set_new_password')
        except PasswordResetOTP.DoesNotExist:
            messages.error(request, 'Invalid OTP entered.')
            # Stay on verify page

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