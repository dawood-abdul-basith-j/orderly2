# smart_features/views.py
from django.db.models import Count
from orders.models import OrderItem, Order
from menu.models import MenuItem, Category
from django.contrib.auth.models import User
from django.shortcuts import render # Add render
from django.contrib.auth.decorators import login_required # Add login_required

# --- Imports for Chatbot ---
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import google.generativeai as genai
import json
# --- End Chatbot Imports ---

# --- Recommendation Functions (Keep these) ---
def get_popular_items(tag_filter=None):
    """
    Finds the top 5 most frequently ordered menu items.
    If tag_filter is provided, filters popular items by that tag.
    """
    # Start with base query
    popular_items_query = OrderItem.objects.filter(
        order__status='Delivered'
    )

    # --- ADD THIS FILTER LOGIC ---
    if tag_filter:
        popular_items_query = popular_items_query.filter(
            menu_item__tags__icontains=tag_filter
        )
    # --- END OF CHANGE ---

    # Continue with aggregation
    popular_items_agg = popular_items_query.values(
        'menu_item_id'
    ).annotate(
        total_orders=Count('id')
    ).order_by(
        '-total_orders'
    )[:5]
    
    item_ids = [item['menu_item_id'] for item in popular_items_agg]
    item_dict = {item.id: item for item in MenuItem.objects.filter(id__in=item_ids)}
    return [item_dict[id] for id in item_ids if id in item_dict]


def get_recommendations(user, tag_filter=None):
    """
    Recommends items from the user's favorite category
    that they have not ordered before.
    If tag_filter is provided, filters recommendations by that tag.
    """
    if not user.is_authenticated:
        return []

    # 1. Find user's favorite category (no change)
    favorite_category = OrderItem.objects.filter(
        order__user=user, order__status='Delivered'
    ).values(
        'menu_item__category'
    ).annotate(
        category_count=Count('id')
    ).order_by(
        '-category_count'
    ).first()
    
    if not favorite_category:
        return []

    fav_category_id = favorite_category['menu_item__category']
    
    # 2. Find items user has already ordered (no change)
    ordered_item_ids = OrderItem.objects.filter(
        order__user=user
    ).values_list('menu_item_id', flat=True).distinct()
    
    # 3. Find items in the favorite category that the user has NOT ordered
    recommendations_query = MenuItem.objects.filter(
        category__id=fav_category_id,
        available=True
    ).exclude(
        id__in=ordered_item_ids
    )

    # --- ADD THIS FILTER LOGIC ---
    if tag_filter:
        recommendations_query = recommendations_query.filter(
            tags__icontains=tag_filter
        )
    # --- END OF CHANGE ---
    
    recommendations = recommendations_query[:5] # Get top 5 of the filtered list
    
    return recommendations

# --- Chatbot Configuration and Views ---

# Configure the Gemini API
if settings.GEMINI_API_KEY:
    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-pro') # Or the model you want to use
        print("Gemini API Configured Successfully.")
    except Exception as e:
        print(f"Error configuring Gemini API: {e}")
        model = None
else:
    print("Gemini API Key not found in settings.")
    model = None # No API key, chatbot won't work

@login_required # View to display the chat page
def chatbot_page_view(request):
    return render(request, 'smart_features/chatbot.html')

@csrf_exempt # API endpoint to handle chat messages
def chatbot_api(request):
    if not model:
        return JsonResponse({'reply': 'Chatbot is not configured (API key missing or configuration error).'}, status=500)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')

            if not user_message:
                return JsonResponse({'reply': 'Empty message received.'}, status=400)

            # --- API Call ---
            # You might want to add context/history here for better conversations
            # Example prompt prefix (optional):
            prompt = f"You are a helpful assistant for the Orderly food ordering app. Answer the following user query concisely: {user_message}"
            response = model.generate_content(prompt) # Send prefixed prompt
            ai_reply = response.text
            # --- End API Call ---

            return JsonResponse({'reply': ai_reply})

        except Exception as e:
            # Basic error handling
            print(f"Chatbot API Error: {e}") # Log the error for debugging
            # Provide a user-friendly error message
            return JsonResponse({'reply': f'Sorry, an error occurred while contacting the AI assistant.'}, status=500)

    return JsonResponse({'error': 'Invalid request method. Use POST.'}, status=405)