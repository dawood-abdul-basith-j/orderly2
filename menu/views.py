# menu/views.py
from django.shortcuts import render, get_object_or_404
from .models import Category, MenuItem, OptionGroup
from django.contrib import messages # Ensure messages is imported if used
from smart_features.views import get_popular_items, get_recommendations
from collections import defaultdict # Import defaultdict
from django.db.models import Q # Import Q for searching

def menu_list_view(request):
    # Get all unique tags for filter buttons
    all_tags_qs = MenuItem.objects.exclude(tags__isnull=True).exclude(tags__exact='').values_list('tags', flat=True).distinct()
    unique_tags = set()
    for tags_string in all_tags_qs:
        unique_tags.update([tag.strip() for tag in tags_string.split(',') if tag.strip()])

    # Base Query, optimize by selecting related category
    menu_items_query = MenuItem.objects.filter(available=True).select_related('category')

    # Apply Tag Filter if present
    tag_filter = request.GET.get('tag')
    if tag_filter:
        menu_items_query = menu_items_query.filter(tags__icontains=tag_filter)

    # Apply Search Query if present
    search_query = request.GET.get('q')
    if search_query:
        menu_items_query = menu_items_query.filter(
            Q(name__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )

    # Group the filtered/searched items by category
    items_by_category = defaultdict(list)
    for item in menu_items_query:
        items_by_category[item.category].append(item)
    # Convert to regular dict sorted by category name for the template
    items_by_category = dict(sorted(items_by_category.items(), key=lambda pair: pair[0].name))

    # Get Recommendations
    popular_items = get_popular_items(tag_filter=tag_filter)
    recommended_items = get_recommendations(request.user, tag_filter=tag_filter)

    context = {
        'items_by_category': items_by_category,
        'popular_items': popular_items,
        'recommended_items': recommended_items,
        'all_tags': sorted(list(unique_tags)),
        'current_tag': tag_filter,
        'search_query': search_query,
    }
    # Removed the test message: messages.info(request, "Testing messages!")
    return render(request, 'menu/menu_list.html', context)


def menu_detail_view(request, item_id):
    menu_item = get_object_or_404(MenuItem, id=item_id)
    # Use prefetch_related for efficiency when accessing options in the template
    option_groups = OptionGroup.objects.filter(menu_item=menu_item).prefetch_related('options')

    context = {
        'item': menu_item,
        'option_groups': option_groups,
    }
    # Ensure the template path is correct relative to the 'templates' directory
    return render(request, 'menu/menu_detail.html', context)