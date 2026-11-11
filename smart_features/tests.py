from django.test import TestCase
from django.contrib.auth.models import User
from menu.models import Category, MenuItem
from orders.models import Order, OrderItem
from smart_features.views import get_popular_items, get_recommendations


class SmartFeaturesTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='smartuser', password='Password123!')
        self.category = Category.objects.create(name='Desserts')
        self.item1 = MenuItem.objects.create(name='Gulab Jamun', category=self.category, price=60.00, tags='sweet')
        self.item2 = MenuItem.objects.create(name='Ice Cream', category=self.category, price=80.00, tags='cold,sweet')

        # Create a delivered order
        order = Order.objects.create(user=self.user, total_amount=120.00, status='Delivered')
        OrderItem.objects.create(order=order, menu_item=self.item1, quantity=2, subtotal=120.00)

    def test_get_popular_items(self):
        popular = get_popular_items()
        self.assertIn(self.item1, popular)

        filtered = get_popular_items(tag_filter='sweet')
        self.assertIn(self.item1, filtered)

    def test_get_recommendations(self):
        # User ordered item1 in Desserts, so item2 (not ordered yet in favorite category) should be recommended
        recommendations = get_recommendations(self.user)
        self.assertIn(self.item2, recommendations)
        self.assertNotIn(self.item1, recommendations)
