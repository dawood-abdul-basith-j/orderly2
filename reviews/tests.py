from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from orders.models import Order
from reviews.models import Review


class ReviewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='reviewer', password='Password123!')
        self.client.login(username='reviewer', password='Password123!')
        self.order = Order.objects.create(user=self.user, total_amount=150.00, status='Delivered')

    def test_add_review_and_prevent_duplicate(self):
        # 1. First review submission
        res = self.client.post(reverse('add_review', args=[self.order.id]), {
            'rating': 5,
            'comment': 'Delicious food and fast delivery!'
        })
        self.assertRedirects(res, reverse('order_status', args=[self.order.id]))

        review = Review.objects.get(order=self.order)
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.comment, 'Delicious food and fast delivery!')

        # 2. Duplicate submission should be prevented
        dup_res = self.client.post(reverse('add_review', args=[self.order.id]), {
            'rating': 4,
            'comment': 'Another review attempt'
        })
        self.assertRedirects(dup_res, reverse('order_status', args=[self.order.id]))
        self.assertEqual(Review.objects.filter(order=self.order).count(), 1)
