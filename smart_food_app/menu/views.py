# menu/views.py
from django.shortcuts import render, get_object_or_404
from .models import Category, MenuItem, OptionGroup
from smart_features.views import get_popular_items, get_recommendations
from collections import defaultdict # Import defaultdict

def menu_list_view(request):
    # --- Get Tags (no change) ---
    all_tags_qs = MenuItem.objects.exclude(tags__isnull=True).exclude(tags__exact='').values_list('tags', flat=True).distinct()
    unique_tags = set()
    for tags_string in all_tags_qs:
        unique_tags.update([tag.strip() for tag in tags_string.split(',') if tag.strip()])

    # --- Filter Items (no change) ---
    menu_items_query = MenuItem.objects.filter(available=True).select_related('category') # Optimize query
    tag_filter = request.GET.get('tag')
    if tag_filter:
        menu_items_query = menu_items_query.filter(tags__icontains=tag_filter)

    # --- NEW: Group Filtered Items by Category ---
    items_by_category = defaultdict(list)
    for item in menu_items_query:
        items_by_category[item.category].append(item)
    # Convert defaultdict to a regular dict for the template, sorting by category name
    items_by_category = dict(sorted(items_by_category.items(), key=lambda pair: pair[0].name))
    # --- END NEW ---

    # --- Recommendations (no change) ---
    popular_items = get_popular_items()
    recommended_items = get_recommendations(request.user)

    context = {
        # 'categories' is no longer needed, we use the keys from items_by_category
        'items_by_category': items_by_category, # Pass the grouped items
        'popular_items': popular_items,
        'recommended_items': recommended_items,
        'all_tags': sorted(list(unique_tags)),
        'current_tag': tag_filter,
    }
    return render(request, 'menu/menu_list.html', context)

# --- Detail View (no change needed here) ---
def menu_detail_view(request, item_id):
    menu_item = get_object_or_404(MenuItem, id=item_id)
    option_groups = OptionGroup.objects.filter(menu_item=menu_item).prefetch_related('options')

    context = {
        'item': menu_item,
        'option_groups': option_groups,
    }
    return render(request, 'menu/menu_detail.html', context)