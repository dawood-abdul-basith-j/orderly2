# payments/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from orders.models import Order
from .models import Payment
from django.utils import timezone # Import timezone

@login_required
def process_online_payment(request):
    order_id = request.session.get('payment_order_id')
    if not order_id:
        messages.error(request, "No order found for payment.")
        return redirect('menu_home')

    order = get_object_or_404(Order, id=order_id, user=request.user, status='Pending')

    # --- For DUMMY/SIMULATION purposes ---
    if request.method == 'POST':
        # Simulate successful payment confirmation
        # 1. Update Order status
        order.status = 'Preparing'
        order.save(update_fields=['status'])

        # 2. Create/Update Payment Record
        Payment.objects.update_or_create(
            order=order,
            defaults={
                'payment_method': 'Online',
                'payment_status': 'Completed',
                'payment_time': timezone.now() # Record payment time
            }
        )

        # 3. Clear session and redirect to success
        if 'payment_order_id' in request.session:
            del request.session['payment_order_id']
        messages.success(request, "Online payment successful! Your order is being prepared.")
        return redirect('order_status', order_id=order.id) # Redirect to standard status page
    # --- END DUMMY ---

    # GET Request: Show the payment form/simulation page
    context = {
        'order': order,
    }
    return render(request, 'payments/payment_form.html', context)

# Optional: A dedicated success page (If you want to use it instead of redirecting to order_status)
# @login_required
# def payment_success(request, order_id):
#    order = get_object_or_404(Order, id=order_id, user=request.user)
#    context = {'order': order}
#    return render(request, 'payments/payment_success.html', context)