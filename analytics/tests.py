from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from orders.models import Order
from payments.models import Payment
from reviews.models import Review


class AnalyticsDashboardTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.regular_user = User.objects.create_user(username='normaluser', password='Password123!')
        self.staff_user = User.objects.create_user(username='adminstaff', password='Password123!', is_staff=True)

        order = Order.objects.create(user=self.regular_user, total_amount=400.00, status='Delivered')
        Payment.objects.create(order=order, payment_method='Online', payment_status='Completed')
        Review.objects.create(order=order, user=self.regular_user, rating=5, comment='Top notch')

    def test_non_staff_redirected(self):
        self.client.login(username='normaluser', password='Password123!')
        res = self.client.get(reverse('analytics_dashboard'))
        self.assertRedirects(res, '/')

    def test_staff_dashboard_metrics(self):
        self.client.login(username='adminstaff', password='Password123!')
        res = self.client.get(reverse('analytics_dashboard'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'Dashboard')
        self.assertIn('total_sales', res.context)
        self.assertEqual(res.context['total_sales'], 400.00)
        self.assertEqual(res.context['total_orders'], 1)
        self.assertEqual(res.context['avg_rating'], 5.0)
