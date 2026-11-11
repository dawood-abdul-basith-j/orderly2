from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from menu.models import Category, MenuItem, OptionGroup, OptionItem
from orders.models import Order, OrderItem


class OrderAndCartTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='orderuser', password='Password123!')
        self.staff_user = User.objects.create_user(username='staffuser', password='Password123!', is_staff=True)
        self.category = Category.objects.create(name='Appetizers')
        self.item = MenuItem.objects.create(
            name='Spring Rolls',
            category=self.category,
            price=120.00,
            available=True,
            avg_prep_time=15
        )
        self.option_group = OptionGroup.objects.create(name='Dip', menu_item=self.item)
        self.option_item = OptionItem.objects.create(name='Sweet Chili', price=15.00, group=self.option_group)
        self.client.login(username='orderuser', password='Password123!')

    def test_add_to_cart_and_view_cart(self):
        # Add item with option
        response = self.client.post(reverse('add_to_cart', args=[self.item.id]), {
            'quantity': 2,
            f'option_group_{self.option_group.id}': self.option_item.id,
            'special_request': 'Extra crispy'
        })
        self.assertRedirects(response, reverse('view_cart'))

        # Cart should have total: (120 + 15) * 2 = 270
        cart = Order.objects.get(user=self.user, status='Pending')
        self.assertEqual(cart.total_amount, 270.00)
        self.assertEqual(cart.orderitem_set.count(), 1)

        cart_view_res = self.client.get(reverse('view_cart'))
        self.assertEqual(cart_view_res.status_code, 200)
        self.assertContains(cart_view_res, 'Spring Rolls')

    def test_remove_from_cart(self):
        self.client.post(reverse('add_to_cart', args=[self.item.id]), {'quantity': 1})
        cart = Order.objects.get(user=self.user, status='Pending')
        order_item = cart.orderitem_set.first()

        remove_res = self.client.get(reverse('remove_from_cart', args=[order_item.id]))
        self.assertRedirects(remove_res, reverse('view_cart'))
        self.assertFalse(Order.objects.filter(id=cart.id).exists())

    def test_cart_sharing_and_join_flow(self):
        # Add item to start cart
        self.client.post(reverse('add_to_cart', args=[self.item.id]), {'quantity': 1})
        share_res = self.client.get(reverse('start_sharing_cart'))
        self.assertRedirects(share_res, reverse('view_cart'))

        cart = Order.objects.get(user=self.user, status='Pending')
        self.assertTrue(bool(cart.share_code))

        # Second user joins group order
        client2 = Client()
        user2 = User.objects.create_user(username='friend', password='Password123!')
        client2.login(username='friend', password='Password123!')

        join_res = client2.get(reverse('join_order', args=[cart.share_code]))
        self.assertRedirects(join_res, '/')

        # Second user adds item to shared cart
        client2.post(reverse('add_to_cart', args=[self.item.id]), {'quantity': 1})
        cart.refresh_from_db()
        self.assertEqual(cart.orderitem_set.count(), 2)

    def test_checkout_cash_flow(self):
        self.client.post(reverse('add_to_cart', args=[self.item.id]), {'quantity': 1})
        cart = Order.objects.get(user=self.user, status='Pending')

        checkout_res = self.client.post(reverse('checkout'), {
            'payment_method': 'Cash',
            'delivery_address': '456 College Road, Coimbatore'
        })
        self.assertRedirects(checkout_res, reverse('order_status', args=[cart.id]))

        cart.refresh_from_db()
        self.assertEqual(cart.status, 'Preparing')
        self.assertEqual(cart.delivery_address, '456 College Road, Coimbatore')
