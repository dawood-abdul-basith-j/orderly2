# smart_food/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('menu/', include('menu.urls')),
    path('orders/', include('orders.urls')),
    path('payments/', include('payments.urls')),
    path('analytics/', include('analytics.urls')), 
    path('smart-features/', include('smart_features.urls')),
    path('reviews/', include('reviews.urls')), # <-- ADD THIS
    path('', include('menu.urls')),
]