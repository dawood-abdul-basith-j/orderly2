# orders/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # --- CORE ORDER FLOW ---
    path('add/<int:item_id>/', views.add_to_cart, name='add_to_cart'), # <<< ADD THIS LINE BACK
    path('cart/', views.view_cart, name='view_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('status/<int:order_id>/', views.order_status, name='order_status'),
    path('remove/<int:order_item_id>/', views.remove_from_cart, name='remove_from_cart'),
    # --- STAFF PANEL ---
    path('panel/', views.order_employee_panel, name='order_employee_panel'),
    path('update-status/<int:order_id>/<str:new_status>/', views.update_order_status, name='update_order_status'),

    # --- GROUP ORDERS ---
    path('start-sharing/', views.start_sharing_cart, name='start_sharing_cart'),
    path('join/<str:share_code>/', views.join_order, name='join_order'),
    path('leave/', views.leave_order, name='leave_order'),
]