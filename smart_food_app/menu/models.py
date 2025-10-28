# menu/models.py
from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class MenuItem(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    available = models.BooleanField(default=True)
    rating = models.FloatField(default=0)
    image_url = models.CharField(max_length=255, blank=True, null=True)
    
    tags = models.CharField(max_length=255, blank=True, help_text="Comma-separated values, e.g., vegan,gluten_free,spicy")
    avg_prep_time = models.PositiveIntegerField(default=10, help_text="Average preparation time in minutes")
    
    def __str__(self):
        return self.name

# --- ADD THESE TWO NEW MODELS ---

class OptionGroup(models.Model):
    """
    A group of options, e.g., "Size", "Add-ons", "Spice Level"
    """
    name = models.CharField(max_length=100)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name="option_groups")

    def __str__(self):
        return f"{self.name} for {self.menu_item.name}"

class OptionItem(models.Model):
    """
    A specific option in a group, e.g., "Medium", "Extra Cheese", "Hot"
    """
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0) # Price for this option
    group = models.ForeignKey(OptionGroup, on_delete=models.CASCADE, related_name="options")

    def __str__(self):
        return f"{self.name} (+₹{self.price})"