# chatbot/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import logging
from .bot_logic import OrderlyChatbot
from orders.models import Order, OrderItem
from menu.models import MenuItem
from django.shortcuts import get_object_or_404
from decimal import Decimal

logger = logging.getLogger(__name__)

# Initialize the chatbot one time when the server starts
try:
    chatbot = OrderlyChatbot()
    logger.info("Chatbot Initialized Successfully.")
except Exception as e:
    logger.error(f"Chatbot Initialization Failed: {e}")
    chatbot = None

@login_required
def chatbot_page_view(request):
    """Renders the HTML page for the chatbot."""
    if not request.session.session_key:
        request.session.create()
    return render(request, 'chatbot/chatbot_interface.html')

@csrf_exempt # Use CSRF token in JS for production
@login_required
def chatbot_api(request):
    """
    Handles POST requests from the chatbot frontend.
    Receives a message, gets a structured response from the bot,
    and performs the action (e.g., modifying the real cart).
    """
    if not chatbot:
        return JsonResponse({"reply": "Chatbot is currently unavailable. Please try again later."}, status=503)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')
            user = request.user

            if not user_message:
                return JsonResponse({'reply': 'Empty message received.'}, status=400)

            # 1. Get structured data from the chatbot
            bot_response = chatbot.handle_message(user_message, user)
            
            # 2. Perform actions based on intent
            bot_reply = bot_response.get('reply', "Sorry, I didn't understand.")
            
            if bot_response.get('intent') == 'add_item':
                item_name = bot_response.get('item_name')
                quantity = int(bot_response.get('quantity', 1))
                if item_name:
                    bot_reply = add_item_to_cart(user, item_name, quantity)

            elif bot_response.get('intent') == 'remove_item':
                item_name = bot_response.get('item_name')
                if item_name:
                    bot_reply = remove_item_from_cart(user, item_name)

            elif bot_response.get('intent') == 'show_cart':
                bot_reply = chatbot.get_cart_context(user) # Get the cart text

            # 3. Send the bot's text reply back to the user
            return JsonResponse({'reply': bot_reply})

        except Exception as e:
            logger.error(f"Error in chatbot_api: {e}")
            return JsonResponse({'reply': 'Sorry, an internal error occurred.'}, status=500)
    
    return JsonResponse({'error': 'Invalid request method. Use POST.'}, status=405)


# --- Helper functions to modify the REAL cart ---

def add_item_to_cart(user, item_name, quantity):
    """Finds the item and adds it to the user's 'Pending' Order."""
    try:
        menu_item = MenuItem.objects.get(name__iexact=item_name, available=True)
    except MenuItem.DoesNotExist:
        return f"Sorry, I couldn't find '{item_name}' on the menu."

    cart, _ = Order.objects.get_or_create(user=user, status='Pending', defaults={'total_amount': 0})
    
    # Check if item has options
    if menu_item.option_groups.exists():
        return f"'{item_name}' has customizations. Please add it from the main menu to select options."

    order_item, created = OrderItem.objects.get_or_create(
        order=cart,
        menu_item=menu_item,
        # We assume no selected options for chatbot orders
        selected_options=None, 
        defaults={'quantity': quantity, 'subtotal': menu_item.price * quantity}
    )

    if not created:
        order_item.quantity += quantity
        order_item.subtotal = order_item.menu_item.price * order_item.quantity
        order_item.save()

    # Recalculate cart total
    cart.total_amount = sum(item.subtotal for item in cart.orderitem_set.all())
    cart.save()
    
    return f"Added {quantity}x {item_name} to your cart."

def remove_item_from_cart(user, item_name):
    """Removes an item from the user's 'Pending' Order."""
    try:
        cart = Order.objects.get(user=user, status='Pending')
        order_item = cart.orderitem_set.get(menu_item__name__iexact=item_name)
        
        item_name = order_item.menu_item.name # Get proper name
        order_item.delete()
        
        # Recalculate cart total
        cart.total_amount = sum(item.subtotal for item in cart.orderitem_set.all())
        cart.save()
        return f"Removed {item_name} from your cart."
        
    except Order.DoesNotExist:
        return "Your cart is empty."
    except OrderItem.DoesNotExist:
        return f"I couldn't find '{item_name}' in your cart."