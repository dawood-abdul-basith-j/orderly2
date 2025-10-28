# orders/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Order, OrderItem
from datetime import timedelta
# --- Import OptionItem ---
from menu.models import MenuItem, OptionItem
from django.utils import timezone
from payments.models import Payment
from django.contrib import messages

# orders/views.py
# ... (imports) ...

@login_required
def add_to_cart(request, item_id):
    if request.method == 'POST':
        menu_item = get_object_or_404(MenuItem, id=item_id)
        quantity = int(request.POST.get('quantity', 1))
        special_request = request.POST.get('special_request', '')
        # ... (calculate price and get options text - no change needed here) ...
        total_option_price = 0
        selected_options_list = []
        for key, value in request.POST.items():
            if key.startswith('option_group_'):
                option = get_object_or_404(OptionItem, id=int(value))
                total_option_price += option.price
                selected_options_list.append(f"{option.group.name}: {option.name}")
        selected_options_text = ", ".join(selected_options_list)
        subtotal = (menu_item.price + total_option_price) * quantity

        # --- MODIFIED: Check for shared order ---
        shared_order_id = request.session.get('shared_order_id')
        if shared_order_id:
            # Add to the existing shared order
            order = get_object_or_404(Order, id=shared_order_id, status='Pending')
            # Ensure the order owner isn't blocked somehow (optional check)
        else:
            # Find or create the user's OWN cart (original logic)
            order, _ = Order.objects.get_or_create(
                user=request.user,
                status='Pending',
                defaults={'total_amount': 0}
            )
        # --- END MODIFICATION ---

        # Create the OrderItem (same logic)
        OrderItem.objects.create(
            order=order,
            menu_item=menu_item,
            quantity=quantity,
            subtotal=subtotal,
            selected_options=selected_options_text,
            special_request=special_request
        )

        # Recalculate total (same logic)
        all_items_in_cart = order.orderitem_set.all()
        order.total_amount = sum(item.subtotal for item in all_items_in_cart)
        order.save()

        # Redirect to the cart of the order we added to
        # If shared, redirect to THEIR cart view (or maybe menu?)
        if shared_order_id:
             messages.success(request, f"{menu_item.name} added to group order {order.share_code}.")
             return redirect('menu_home') # Redirect to menu after adding to shared cart
        else:
             return redirect('view_cart') # Redirect to own cart

    return redirect('menu_home')

# ... (rest of the views) ...

@login_required
def view_cart(request):
    cart = Order.objects.filter(user=request.user, status='Pending').first()
    share_link = None # Initialize share_link

    if cart and cart.share_code:
        # Construct the full share link if code exists
        share_link = request.build_absolute_uri(f'/orders/join/{cart.share_code}/')

    cart_items = []
    if cart:
        cart_items = cart.orderitem_set.all()

    context = {
        'cart': cart,
        'cart_items': cart_items,
        'share_link': share_link, # Pass link to template
    }
    return render(request, 'orders/cart.html', context)

@login_required
def checkout(request):
    cart = Order.objects.filter(user=request.user, status='Pending').first()

    if not cart or not cart.orderitem_set.all():
        return redirect('menu_home')

    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')

        if payment_method == 'Cash':
            # --- CALCULATE ESTIMATED PREP TIME ---
            total_estimated_prep_time = 0
            for item in cart.orderitem_set.select_related('menu_item'):
                # Use the average prep time stored on the menu item
                total_estimated_prep_time += item.menu_item.avg_prep_time * item.quantity

            # --- CALCULATE ESTIMATED DELIVERY TIME ---
            # Add prep time + a buffer for delivery (e.g., 30 minutes)
            delivery_buffer_minutes = 30
            estimated_delivery = timezone.now() + timedelta(minutes=total_estimated_prep_time + delivery_buffer_minutes)
            # --- END CALCULATIONS ---

            # 1. Update the order status AND save estimate
            cart.status = 'Preparing'
            cart.order_time = timezone.now()
            cart.estimated_delivery_time = estimated_delivery # Save the estimate
            cart.save(update_fields=['status', 'order_time', 'estimated_delivery_time']) # Be explicit

            # 2. Create a Payment record
            Payment.objects.create(
                order=cart,
                payment_method='Cash',
                payment_status='Pending'
            )

            # 3. Redirect to an order confirmation/status page
            return redirect('order_status', order_id=cart.id)
        else:
            pass # Handle other payment methods later

    context = {
        'cart': cart,
        'cart_items': cart.orderitem_set.all()
    }
    return render(request, 'orders/checkout.html', context)

@login_required
def order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    context = {
        'order': order
    }
    return render(request, 'orders/order_status.html', context)

@login_required
def order_employee_panel(request):
    # This view is for staff. We should add a check here.
    if not request.user.is_staff:
        return redirect('menu_home') # Redirect non-staff users

    # Get all orders that are not in cart and not delivered
    active_orders = Order.objects.exclude(status='Pending').exclude(status='Delivered').order_by('-order_time')
    
    context = {
        'active_orders': active_orders
    }
    return render(request, 'orders/order_employee_panel.html', context)

@login_required
def update_order_status(request, order_id, new_status):
    if not request.user.is_staff:
        return redirect('menu_home')

    order = get_object_or_404(Order, id=order_id)
    now = timezone.now()

    # --- UPDATE LOGIC TO RECORD TIMES ---
    if new_status == 'Cooking' and not order.cooking_start_time:
        order.cooking_start_time = now
    elif new_status == 'Ready' and not order.cooking_end_time:
        order.cooking_end_time = now
    elif new_status == 'Delivered' and not order.actual_delivery_time:
        order.actual_delivery_time = now
        # Also update payment if paid with cash
        payment = Payment.objects.filter(order=order, payment_method='Cash').first()
        if payment:
            payment.payment_status = 'Completed'
            payment.save()
    # --- END UPDATE ---

    # Update the status itself
    order.status = new_status
    order.save(update_fields=['status', 'cooking_start_time', 'cooking_end_time', 'actual_delivery_time']) # Be explicit

    # --- Optional: Trigger background task to update avg_prep_time here ---
    # if new_status == 'Ready':
    #    update_average_prep_times(order) # We'll define this later if needed

    return redirect('order_employee_panel')

@login_required
def start_sharing_cart(request):
    cart = Order.objects.filter(user=request.user, status='Pending').first()
    if cart:
        cart.generate_share_code() # Call the method we added to the model
        messages.success(request, f"Cart sharing started! Share this code: {cart.share_code}")
    else:
        messages.error(request, "Your cart is empty.")
    return redirect('view_cart')

@login_required
def join_order(request, share_code):
    # Find the order being shared
    order_to_join = get_object_or_404(Order, share_code=share_code.upper(), status='Pending')

    # Check if the current user already has items in this order (optional)
    # You could add logic here to prevent duplicate joins or merge carts

    # Store the ID of the shared order in the user's session
    request.session['shared_order_id'] = order_to_join.id
    request.session['shared_order_code'] = share_code.upper() # Store code for display

    messages.success(request, f"You have joined the group order ({share_code.upper()}). Items you add will go to this shared cart.")
    return redirect('menu_home') # Redirect to menu to start adding items

# --- Add a view to leave a shared order ---
@login_required
def leave_order(request):
    if 'shared_order_id' in request.session:
        del request.session['shared_order_id']
        del request.session['shared_order_code']
        messages.info(request, "You have left the group order.")
    return redirect('menu_home')