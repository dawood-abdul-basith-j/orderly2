# reviews/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Review
from orders.models import Order
from django.contrib import messages

@login_required
def add_review(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    # Check if a review already exists for this order
    # We use hasattr() to check for the reverse relationship
    if hasattr(order, 'review'):
        messages.error(request, "You have already submitted a review for this order.")
        return redirect('order_status', order_id=order.id)

    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')

        Review.objects.create(
            order=order,
            user=request.user,
            rating=rating,
            comment=comment
        )
        
        messages.success(request, "Thank you for your review!")
        return redirect('order_status', order_id=order.id)

    context = {
        'order': order
    }
    return render(request, 'reviews/add_review.html', context)