from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from orders.models import Order
from payments.models import Payment


class PaymentTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='payuser', password='Password123!')
        self.client.login(username='payuser', password='Password123!')
        self.order = Order.objects.create(
            user=self.user,
            total_amount=350.00,
            status='Pending'
        )

    def test_process_online_payment_flow(self):
        # Set session payment_order_id
        session = self.client.session
        session['payment_order_id'] = self.order.id
        session.save()

        get_res = self.client.get(reverse('process_online_payment'))
        self.assertEqual(get_res.status_code, 200)

        post_res = self.client.post(reverse('process_online_payment'))
        self.assertRedirects(post_res, reverse('order_status', args=[self.order.id]))

        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'Preparing')

        payment = Payment.objects.get(order=self.order)
        self.assertEqual(payment.payment_method, 'Online')
        self.assertEqual(payment.payment_status, 'Completed')
