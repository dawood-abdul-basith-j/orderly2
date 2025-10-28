# orders/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # ... (add_to_cart, cart, checkout, status, panel, update-status) ...
    path('panel/', views.order_employee_panel, name='order_employee_panel'),
    path('update-status/<int:order_id>/<str:new_status>/', views.update_order_status, name='update_order_status'),

    # --- ADD THESE ---
    path('cart/', views.view_cart, name='view_cart'),
    path('start-sharing/', views.start_sharing_cart, name='start_sharing_cart'),
    path('join/<str:share_code>/', views.join_order, name='join_order'),
    path('leave/', views.leave_order, name='leave_order'),
]