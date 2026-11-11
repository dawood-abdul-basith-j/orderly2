from django.core.management.base import BaseCommand
from menu.models import Category, MenuItem, OptionGroup, OptionItem


class Command(BaseCommand):
    help = 'Seeds sample categories, menu items, and customization options'

    def handle(self, *args, **options):
        self.stdout.write("Seeding sample menu data...")

        # 1. Categories
        cat_starters, _ = Category.objects.get_or_create(
            name='Starters & Appetizers',
            defaults={'description': 'Delicious finger foods and appetizers'}
        )
        cat_mains, _ = Category.objects.get_or_create(
            name='Main Course',
            defaults={'description': 'Hearty curries, biryanis, and platters'}
        )
        cat_breads, _ = Category.objects.get_or_create(
            name='Breads & Rice',
            defaults={'description': 'Freshly baked tandoori breads and aromatic rice'}
        )
        cat_desserts, _ = Category.objects.get_or_create(
            name='Beverages & Desserts',
            defaults={'description': 'Refreshing drinks and sweet treats'}
        )

        # 2. Menu Items
        items_data = [
            {
                'name': 'Crispy Spring Rolls',
                'category': cat_starters,
                'price': 140.00,
                'available': True,
                'rating': 4.6,
                'tags': 'vegetarian,crispy,popular',
                'avg_prep_time': 12,
                'options': [
                    {'group': 'Dip Choice', 'items': [('Sweet Chili', 0), ('Garlic Mayo', 15), ('Mint Chutney', 10)]}
                ]
            },
            {
                'name': 'Chicken Tikka',
                'category': cat_starters,
                'price': 220.00,
                'available': True,
                'rating': 4.8,
                'tags': 'non_veg,tandoori,spicy,popular',
                'avg_prep_time': 15,
                'options': [
                    {'group': 'Spice Level', 'items': [('Mild', 0), ('Medium Spicy', 0), ('Extra Hot', 10)]}
                ]
            },
            {
                'name': 'Special Chicken Biryani',
                'category': cat_mains,
                'price': 280.00,
                'available': True,
                'rating': 4.9,
                'tags': 'non_veg,biryani,spicy,bestseller',
                'avg_prep_time': 20,
                'options': [
                    {'group': 'Portion Size', 'items': [('Regular', 0), ('Large (Serves 2)', 100)]},
                    {'group': 'Extra Add-ons', 'items': [('Extra Egg', 20), ('Extra Raita', 25)]}
                ]
            },
            {
                'name': 'Paneer Butter Masala',
                'category': cat_mains,
                'price': 240.00,
                'available': True,
                'rating': 4.7,
                'tags': 'vegetarian,gravy,paneer',
                'avg_prep_time': 15,
                'options': [
                    {'group': 'Spice Level', 'items': [('Mild', 0), ('Medium', 0), ('Spicy', 0)]}
                ]
            },
            {
                'name': 'Butter Naan',
                'category': cat_breads,
                'price': 45.00,
                'available': True,
                'rating': 4.5,
                'tags': 'vegetarian,tandoor',
                'avg_prep_time': 5,
                'options': []
            },
            {
                'name': 'Garlic Naan',
                'category': cat_breads,
                'price': 60.00,
                'available': True,
                'rating': 4.7,
                'tags': 'vegetarian,tandoor,garlic',
                'avg_prep_time': 6,
                'options': []
            },
            {
                'name': 'Mango Lassi',
                'category': cat_desserts,
                'price': 90.00,
                'available': True,
                'rating': 4.8,
                'tags': 'vegetarian,cold,sweet,beverage',
                'avg_prep_time': 5,
                'options': []
            },
            {
                'name': 'Warm Gulab Jamun (2 pcs)',
                'category': cat_desserts,
                'price': 70.00,
                'available': True,
                'rating': 4.9,
                'tags': 'vegetarian,sweet,dessert',
                'avg_prep_time': 5,
                'options': [
                    {'group': 'Served With', 'items': [('Plain', 0), ('With Vanilla Ice Cream', 40)]}
                ]
            },
        ]

        for item_info in items_data:
            item, created = MenuItem.objects.get_or_create(
                name=item_info['name'],
                category=item_info['category'],
                defaults={
                    'price': item_info['price'],
                    'available': item_info['available'],
                    'rating': item_info['rating'],
                    'tags': item_info['tags'],
                    'avg_prep_time': item_info['avg_prep_time'],
                }
            )

            # Add OptionGroups and OptionItems
            for og_data in item_info['options']:
                og, _ = OptionGroup.objects.get_or_create(
                    name=og_data['group'],
                    menu_item=item
                )
                for opt_name, opt_price in og_data['items']:
                    OptionItem.objects.get_or_create(
                        name=opt_name,
                        group=og,
                        defaults={'price': opt_price}
                    )

        self.stdout.write(self.style.SUCCESS("Successfully seeded menu items and categories!"))

