# reviews/models.py
from django.db import models
from django.contrib.auth.models import User
from orders.models import Order
from django.core.validators import MaxValueValidator, MinValueValidator

class Review(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE) # One review per order
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for Order {self.order.id} by {self.user.username}"