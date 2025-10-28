import unittest

from .bot_logic import OrderlyChatbot


class ChatbotParserTests(unittest.TestCase):
	def setUp(self):
		# Initialize without API key so it uses the fallback parser
		self.bot = OrderlyChatbot(api_key=None)

	def test_greeting(self):
		res = self.bot.handle_message("hi", None)
		self.assertIsInstance(res, dict)
		self.assertEqual(res.get("intent"), "general_query")
		self.assertIn("Hello", res.get("reply", ""))

	def test_add_and_remove_parsing(self):
		add = self.bot._simple_parser("add 2 chicken biryani")
		self.assertEqual(add.get("intent"), "add_item")
		self.assertEqual(add.get("quantity"), 2)

		remove = self.bot._simple_parser("remove 1 chicken biryani")
		self.assertEqual(remove.get("intent"), "remove_item")
		self.assertEqual(remove.get("quantity"), 1)