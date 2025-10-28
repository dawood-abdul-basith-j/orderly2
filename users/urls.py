# users/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('settings/', views.settings_view, name='settings'),

    

    # Password reset URLs
    path('password-reset/request/', views.request_password_reset_otp, name='request_otp'),
    path('password-reset/verify/', views.verify_password_reset_otp, name='verify_reset_otp'),
    path('password-reset/set-new/', views.set_new_password, name='set_new_password'),
]