# smart_features/views.py
from django.db.models import Count
from orders.models import OrderItem, Order
from menu.models import MenuItem, Category
from django.contrib.auth.models import User

def get_popular_items():
    """
    Finds the top 5 most frequently ordered menu items
    across all 'Delivered' orders.
    """
    popular_items = OrderItem.objects.filter(
        order__status='Delivered'
    ).values(
        'menu_item_id' # Group by item
    ).annotate(
        total_orders=Count('id') # Count occurrences
    ).order_by(
        '-total_orders' # Order by most popular
    )[:5] # Get top 5
    
    # Get the actual MenuItem objects from the IDs
    item_ids = [item['menu_item_id'] for item in popular_items]
    # Preserve order of IDs
    item_dict = {item.id: item for item in MenuItem.objects.filter(id__in=item_ids)}
    return [item_dict[id] for id in item_ids if id in item_dict]

def get_recommendations(user):
    """
    Recommends items from the user's favorite category
    that they have not ordered before.
    """
    if not user.is_authenticated:
        return []

    # 1. Find user's favorite category
    favorite_category = OrderItem.objects.filter(
        order__user=user, order__status='Delivered'
    ).values(
        'menu_item__category' # Group by category
    ).annotate(
        category_count=Count('id') # Count orders per category
    ).order_by(
        '-category_count' # Order by highest count
    ).first()
    
    if not favorite_category:
        return [] # No order history, no recommendations

    fav_category_id = favorite_category['menu_item__category']
    
    # 2. Find items user has already ordered
    ordered_item_ids = OrderItem.objects.filter(
        order__user=user
    ).values_list('menu_item_id', flat=True).distinct()
    
    # 3. Find items in the favorite category that the user has NOT ordered
    recommendations = MenuItem.objects.filter(
        category__id=fav_category_id,
        available=True
    ).exclude(
        id__in=ordered_item_ids
    )[:5] # Get up to 5 recommendations
    
    return recommendations