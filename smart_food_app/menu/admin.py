# menu/admin.py
from django.contrib import admin
from .models import Category, MenuItem, OptionGroup, OptionItem # Import new models

# Register your models here.
admin.site.register(Category)
admin.site.register(MenuItem)
admin.site.register(OptionGroup) # <-- ADD THIS
admin.site.register(OptionItem)  # <-- ADD THIS