from django.db import models
from orders.models import Order

class Payment(models.Model):
    PAYMENT_METHODS = [
        ('Cash', 'Cash'),
        ('Card', 'Card'),
        ('UPI', 'UPI'),
    ]
    PAYMENT_STATUS = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHODS)
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS, default='Pending')
    payment_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.id} for Order {self.order.id}"
