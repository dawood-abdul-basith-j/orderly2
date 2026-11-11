from django.test import TestCase, Client
from menu.models import Category, MenuItem, OptionGroup, OptionItem


class MenuModelAndViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name='Main Course', description='Main dishes')
        self.item = MenuItem.objects.create(
            name='Chicken Biryani',
            category=self.category,
            price=250.00,
            available=True,
            tags='spicy,non_veg',
            avg_prep_time=25
        )
        self.option_group = OptionGroup.objects.create(name='Portion Size', menu_item=self.item)
        self.option_item = OptionItem.objects.create(name='Large', price=50.00, group=self.option_group)

    def test_menu_models(self):
        self.assertEqual(str(self.category), 'Main Course')
        self.assertEqual(str(self.item), 'Chicken Biryani')
        self.assertEqual(str(self.option_group), 'Portion Size for Chicken Biryani')
        self.assertIn('Large', str(self.option_item))

    def test_menu_list_view(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Chicken Biryani')

    def test_menu_list_search(self):
        response = self.client.get('/?q=Biryani')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Chicken Biryani')

        response_empty = self.client.get('/?q=NonExistentPizza')
        self.assertEqual(response_empty.status_code, 200)
        self.assertNotContains(response_empty, 'Chicken Biryani')

    def test_menu_list_tag_filter(self):
        response = self.client.get('/?tag=spicy')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Chicken Biryani')

    def test_menu_detail_view(self):
        response = self.client.get(f'/menu/item/{self.item.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Chicken Biryani')
        self.assertContains(response, 'Portion Size')
        self.assertContains(response, 'Large')

