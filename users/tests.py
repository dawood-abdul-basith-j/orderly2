from django.test import TestCase, Client
from django.contrib.auth.models import User
from users.models import Profile, PasswordResetOTP
from users.forms import SignUpForm, ProfileUpdateForm
from django.utils import timezone
from datetime import timedelta


class UserAuthenticationAndProfileTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='Password123!',
            first_name='Test',
            last_name='User'
        )
        self.profile = Profile.objects.create(
            user=self.user,
            phone='+919876543210',
            mobile_number='+919876543210'
        )

    def test_signup_form_commit_false_and_true(self):
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'mobile_number': '+919999988888',
            'first_name': 'New',
            'last_name': 'User',
            'password1': 'ValidPassword123!',
            'password2': 'ValidPassword123!',
        }
        form = SignUpForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)

        # Test commit=False does not crash with Model instances passed to related filters must be saved
        unsaved_user = form.save(commit=False)
        self.assertIsNone(unsaved_user.pk)
        unsaved_user.save()
        if hasattr(form, 'save_m2m'):
            form.save_m2m()

        profile = Profile.objects.get(user=unsaved_user)
        self.assertEqual(profile.mobile_number, '+919999988888')
        self.assertEqual(profile.phone, '+919999988888')

    def test_login_with_username(self):
        response = self.client.post('/users/login/', {
            'username': 'testuser',
            'password': 'Password123!'
        })
        self.assertRedirects(response, '/', target_status_code=200)

    def test_login_with_mobile_number(self):
        response = self.client.post('/users/login/', {
            'username': '+919876543210',
            'password': 'Password123!'
        })
        self.assertRedirects(response, '/', target_status_code=200)

    def test_profile_update_form_syncs_phone(self):
        form = ProfileUpdateForm(instance=self.profile, data={
            'phone': '+918888877777',
            'address': '123 Test St',
            'dietary_preference': 'vegetarian'
        })
        self.assertTrue(form.is_valid(), form.errors)
        saved_profile = form.save()
        self.assertEqual(saved_profile.phone, '+918888877777')
        self.assertEqual(saved_profile.mobile_number, '+918888877777')

    def test_password_reset_otp_expiry(self):
        otp = PasswordResetOTP.objects.create(
            user=self.user,
            otp='123456'
        )
        self.assertFalse(otp.is_expired())

        # Manually expire
        otp.expires_at = timezone.now() - timedelta(minutes=1)
        otp.save()
        self.assertTrue(otp.is_expired())

    def test_full_password_reset_otp_flow(self):
        # 1. Request OTP
        req_res = self.client.post('/users/password-reset/request/', {
            'email': 'test@example.com'
        })
        self.assertRedirects(req_res, '/users/password-reset/verify/')

        # Retrieve generated OTP
        otp_obj = PasswordResetOTP.objects.get(user=self.user)
        self.assertIsNotNone(otp_obj.otp)

        # 2. Verify OTP
        verify_res = self.client.post('/users/password-reset/verify/', {
            'otp': otp_obj.otp
        })
        self.assertRedirects(verify_res, '/users/password-reset/set-new/')

        # 3. Set new password
        set_pw_res = self.client.post('/users/password-reset/set-new/', {
            'new_password1': 'NewSecretPassword123!',
            'new_password2': 'NewSecretPassword123!',
        })
        self.assertRedirects(set_pw_res, '/users/login/')

        # 4. Verify login with new password
        login_res = self.client.post('/users/login/', {
            'username': 'testuser',
            'password': 'NewSecretPassword123!'
        })
        self.assertRedirects(login_res, '/', target_status_code=200)
