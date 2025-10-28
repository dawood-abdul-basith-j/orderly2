# orders/models.py
from django.db import models
from django.contrib.auth.models import User # Make sure User is imported
from menu.models import MenuItem
import uuid

class Order(models.Model):
    # ... (your existing Order model is fine) ...
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Preparing', 'Preparing'),
        ('Cooking', 'Cooking'),         # --- ADD THIS --- In progress
        ('Ready', 'Ready'),
        ('Out for delivery', 'Out for delivery'),
        ('Delivered', 'Delivered'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    order_time = models.DateTimeField(auto_now_add=True)
    cooking_start_time = models.DateTimeField(null=True, blank=True)
    cooking_end_time = models.DateTimeField(null=True, blank=True) # When ready for delivery
    estimated_delivery_time = models.DateTimeField(null=True, blank=True)
    actual_delivery_time = models.DateTimeField(null=True, blank=True) # When marked delivered
    share_code = models.CharField(max_length=8, unique=True, null=True, blank=True, help_text="Unique code for sharing the cart")
    delivery_address = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return f"Order {self.id} by {self.user.username}"
    
    def generate_share_code(self):
        if not self.share_code:
            # Generate a short, unique code (e.g., first 8 chars of UUID)
            self.share_code = str(uuid.uuid4())[:8].upper()
            self.save(update_fields=['share_code'])
        return self.share_code


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    subtotal = models.DecimalField(max_digits=8, decimal_places=2)
    
    # --- ADD THESE TWO NEW FIELDS ---
    selected_options = models.TextField(blank=True, null=True) # Stores a summary of chosen options
    special_request = models.TextField(blank=True, null=True) # For user notes like "no onions"

    def __str__(self):
        return f"{self.quantity} x {self.menu_item.name}"