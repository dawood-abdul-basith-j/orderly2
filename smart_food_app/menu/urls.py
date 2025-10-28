# menu/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.menu_list_view, name='menu_home'),
    # --- ADD THIS NEW URL ---
    path('item/<int:item_id>/', views.menu_detail_view, name='menu_detail'),
]