# chatbot/bot_logic.py
"""Chatbot logic for Orderly.

This file provides a robust chatbot wrapper that will use Google
Gemini if available and configured, otherwise it falls back to a
simple rule-based parser so the app doesn't crash when API/key
is missing.
"""

import os
import re
import json
import logging
from decimal import Decimal
from django.conf import settings
from django.db import models

# Try to import the Google generative API client. If unavailable,
# we'll operate in offline/fallback mode.
try:
    import google.generativeai as genai  # type: ignore
except Exception:
    genai = None

# Import models lazily inside functions to avoid importing Django models
# at module import time which requires DJANGO_SETTINGS_MODULE to be set.

logger = logging.getLogger(__name__)


class OrderlyChatbot:
    """Orderly chatbot with graceful fallback.

    Behavior:
    - If a valid GEMINI API key is present and the `google-generativeai`
      package can be imported, the chatbot will be marked as "online"
      and an attempt to use the API may be made.
    - Otherwise, a simple rule-based parser will be used so the
      application continues to work without external AI connectivity.
    """

    def __init__(self, api_key: str | None = None):
        # prefer explicit api_key argument, else use settings/env
        if api_key is not None:
            self.api_key = api_key
        else:
            try:
                self.api_key = getattr(settings, "GEMINI_API_KEY", os.getenv("GEMINI_API_KEY"))
            except Exception:
                # settings may not be configured (e.g., during quick local tests)
                self.api_key = os.getenv("GEMINI_API_KEY")

        self.has_genai = bool(genai and self.api_key)
        if self.has_genai:
            try:
                genai.configure(api_key=self.api_key)
                logger.info("Gemini client configured for OrderlyChatbot.")
            except Exception as e:
                logger.warning("Failed to configure Gemini client: %s", e)
                self.has_genai = False

        if not self.has_genai:
            logger.info("Gemini not available or API key missing. Using fallback parser.")

        # build a system prompt only when needed (defer heavy DB ops)
        self.system_prompt = None

    def _build_system_prompt(self) -> str:
        """Builds the system prompt from the database. Called lazily."""
        if self.system_prompt:
            return self.system_prompt

        menu_text = "RESTAURANT MENU:\n\n"
        try:
            from menu.models import Category

            categories = Category.objects.all().prefetch_related("menuitem_set")
            for category in categories:
                menu_text += f"Category: {category.name}\n"
                items = category.menuitem_set.filter(available=True)
                if not items:
                    menu_text += "  - (No items currently available)\n"
                for item in items:
                    menu_text += f"  - Item Name: \"{item.name}\", Price: {item.price}, ID: {item.id}\n"
                menu_text += "\n"

            from orders.models import OrderItem

            popular_items_query = (
                OrderItem.objects.values("menu_item__name")
                .annotate(count=models.Count("id"))
                .order_by("-count")[:5]
            )
            popular_text = "POPULAR ITEMS: " + ", ".join([item["menu_item__name"] for item in popular_items_query])
        except Exception as e:
            logger.warning("Error while building system prompt: %s", e)
            popular_text = "POPULAR ITEMS: N/A"

        self.system_prompt = (
            "You are Orderly, a helpful food ordering assistant.\n"
            + menu_text
            + "\n"
            + popular_text
            + "\n\nIMPORTANT RULES:\n1. Identify user intent: add_item/remove_item/show_cart/general_query.\n"
            + "2. When add/remove: identify item_name and quantity (default 1).\n3. Try not to hallucinate menu items. If unsure, ask for clarification.\n"
            + "JSON Response Format:\n{\n  \"intent\": \"...\",\n  \"item_name\": \"...\",\n  \"quantity\": X,\n  \"reply\": \"...\"\n}\n"
        )

        return self.system_prompt

    def get_cart_context(self, user) -> str:
        """Returns a short textual summary of the user's pending cart.

        This function is defensive: if `user` is None or DB access fails,
        it returns a sensible default string so callers won't error.
        """
        cart_context = "\nCURRENT CART:\n"
        if not user:
            cart_context += "Your cart is empty.\n"
            return cart_context

        try:
            from orders.models import Order

            cart = Order.objects.get(user=user, status="Pending")
            if not cart.orderitem_set.exists():
                cart_context += "Your cart is empty.\n"
            else:
                for item in cart.orderitem_set.all():
                    cart_context += f"- {item.quantity}x {item.menu_item.name}\n"
                cart_context += f"Total: ₹{cart.total_amount}\n"
        except Order.DoesNotExist:
            cart_context += "Your cart is empty.\n"
        except Exception as e:
            logger.warning("Error fetching cart context: %s", e)
            cart_context += "(Unable to retrieve cart)\n"

        return cart_context

    # --- Simple rule-based parser as a fallback ---
    def _simple_parser(self, message: str) -> dict:
        """Very small intent parser for common commands.

        Returns a dict with keys: intent, item_name, quantity, reply
        """
        text = (message or "").strip()
        lower = text.lower()

    # greetings
        if any(w in lower for w in ("hi", "hello", "hey")) and len(lower.split()) <= 2:
            return {
                "intent": "general_query",
                "item_name": None,
                "quantity": None,
                "reply": "Hello! I'm Orderly's AI assistant. How can I help? (e.g., show menu, add spring rolls, what are popular items?)",
            }

        # show cart
        if "cart" in lower or "what's in my cart" in lower or "my cart" in lower:
            return {"intent": "show_cart", "item_name": None, "quantity": None, "reply": "Showing your cart."}

        # add item patterns: "add 2 chicken biryani" or "add chicken biryani"
        m = re.search(r"add\s*(\d+)?\s*(?:x|times|\s)?\s*(.+)", lower)
        if m:
            qty = int(m.group(1)) if m.group(1) else 1
            item = m.group(2).strip()
            # try to map to a menu item by case-insensitive exact match
            try:
                from menu.models import MenuItem

                menu_item = MenuItem.objects.filter(name__iexact=item, available=True).first()
                item_name = menu_item.name if menu_item else item.title()
            except Exception:
                item_name = item.title()

            return {
                "intent": "add_item",
                "item_name": item_name,
                "quantity": qty,
                "reply": f"Okay, adding {qty}x {item_name} to your cart (via chatbot).",
            }

        # remove item patterns
        m = re.search(r"(?:remove|delete|subtract)\s*(\d+)?\s*(.+)", lower)
        if m:
            qty = int(m.group(1)) if m.group(1) else 1
            item = m.group(2).strip()
            try:
                from menu.models import MenuItem

                menu_item = MenuItem.objects.filter(name__iexact=item).first()
                item_name = menu_item.name if menu_item else item.title()
            except Exception:
                item_name = item.title()

            return {"intent": "remove_item", "item_name": item_name, "quantity": qty, "reply": f"Removing {qty}x {item_name} from your cart."}

        # fallback general response
        return {"intent": "general_query", "item_name": None, "quantity": None, "reply": "I didn't understand exactly — could you rephrase or be more specific?"}

    def handle_message(self, user_message: str, user) -> dict:
        """Handle an incoming message and return a structured response dict.

        If Gemini is available, you may choose to call the API here. For
        stability we default to the simple parser and only call the external
        API in a try/except block (not used by default in this change).
        """
        # Defensive: ensure message is a string
        user_message = (user_message or "").strip()


        # 1) Prefer the local parser so the site never depends on Gemini.
        try:
            parsed = self._simple_parser(user_message)
            # If show_cart intent, replace reply with actual cart context
            if parsed.get("intent") == "show_cart":
                cart_text = self.get_cart_context(user)
                parsed["reply"] = cart_text

            # 2) If Gemini is available, attempt a guarded external call to
            # refine/replace the parsed result. Any failure should be logged
            # and the local parser result should be returned as a fallback.
            if self.has_genai:
                try:
                    # Build a fuller prompt and call Gemini in a try/except.
                    cart_context = self.get_cart_context(user)
                    full_prompt = f"{self._build_system_prompt()}\n{cart_context}\nUser: \"{user_message}\"\nResponse:"

                    # Create a model locally to avoid holding state at import time.
                    # Allow overriding the model id via environment or Django settings
                    # so you can switch models without changing code.
                    model_name = os.getenv("GEMINI_MODEL")
                    try:
                        model_name = model_name or getattr(settings, "GEMINI_MODEL", None)
                    except Exception:
                        # settings may be unavailable in quick test contexts
                        model_name = model_name or None
                    if not model_name:
                        model_name = "models/gemini-3.8-flash"

                    model = genai.GenerativeModel(model_name)
                    response = model.generate_content(full_prompt)

                    # Extract text field (API may return different shapes)
                    resp_text = getattr(response, "text", None) or str(response)
                    json_text = resp_text.strip().replace("```json", "").replace("```", "").strip()

                    try:
                        external_parsed = json.loads(json_text)
                        if isinstance(external_parsed, dict) and external_parsed.get("intent"):
                            return external_parsed
                    except json.JSONDecodeError:
                        logger.warning("Gemini response not valid JSON, falling back to local parser.")

                except Exception as e:
                    logger.warning("Gemini call failed, using fallback parser: %s", e)

            return parsed

        except Exception as e:
            logger.error("Error in local parser: %s", e)
            return {"intent": "error", "reply": "I apologize, I'm having trouble processing that. Please try again."}

        # NOTE: we intentionally do not call the external Gemini API here by default.
        # If you want to enable it, add a guarded block similar to:
        # if self.has_genai:
        #     try: ... call genai ... except: fallback

