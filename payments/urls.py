# payments/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Ensure this line exists and has the correct name
    path('process/', views.process_online_payment, name='process_online_payment'),
    # Optional success page URL
    # path('success/<int:order_id>/', views.payment_success, name='payment_success'),
]