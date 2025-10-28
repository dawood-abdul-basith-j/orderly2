# analytics/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Avg # Import Avg
from orders.models import Order, OrderItem
from menu.models import MenuItem
from reviews.models import Review # Import the Review model

@login_required
def dashboard_view(request):
    # Only staff can access this page
    if not request.user.is_staff:
        return redirect('menu_home')

    # 1. Total Sales
    total_sales = Order.objects.filter(payment__payment_status='Completed').aggregate(
        total=Sum('total_amount')
    )['total'] or 0.00

    # 2. Total Orders
    total_orders = Order.objects.exclude(status='Pending').count()

    # 3. Top Selling Item
    top_item = OrderItem.objects.values(
        'menu_item__name'
    ).annotate(
        total_sold=Count('id')
    ).order_by(
        '-total_sold'
    ).first()

    top_selling_item = top_item['menu_item__name'] if top_item else "N/A"
    
    # 4. Recent Orders
    recent_orders = Order.objects.exclude(status='Pending').order_by('-order_time')[:5]

    # --- 5. NEW: Average Rating ---
    avg_rating = Review.objects.aggregate(
        average=Avg('rating')
    )['average'] or 0.0
    
    context = {
        'total_sales': total_sales,
        'total_orders': total_orders,
        'top_selling_item': top_selling_item,
        'recent_orders': recent_orders,
        'avg_rating': avg_rating, # Add new data to context
    }
    return render(request, 'analytics/dashboard.html', context)