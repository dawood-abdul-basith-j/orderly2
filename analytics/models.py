from django.db import models

class Analytics(models.Model):
    report_name = models.CharField(max_length=100)
    generated_at = models.DateTimeField(auto_now_add=True)
    total_sales = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total_orders = models.IntegerField(blank=True, null=True)
    top_selling_item = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.report_name
