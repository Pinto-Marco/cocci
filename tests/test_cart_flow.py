from __future__ import annotations
import pytest
from django.urls import reverse
from orders.models import CartItem, Order


@pytest.mark.django_db
class TestCartFlow:
    def test_add_to_cart(self, api_client, product_factory):
        product = product_factory(code="C001", price=50.0)
        url = reverse("add-to-cart-api")

        # Ensure session exists
        session = api_client.session
        session.create()
        session.save()

        # Test add
        response = api_client.post(
            url, {"product_code": product.code, "quantity": 2}, format="json"
        )
        assert response.status_code == 200

        # Verify DB
        # We need session_id logic to be consistent.
        # APIClient maintains session.
        session_id = api_client.session.session_key or api_client.session.create()
        # Wait, get_or_create_cart_id logic effectively uses session_key.
        # But api_client.session might be mock or needs save.

        # Actually in views.py: request.session['cart_id'] = ...
        # So we should check if session has cart_id
        # assert 'cart_id' in api_client.session

        # Let's check CartItem directly assuming usage of session_key
        # Since middleware is involved, let's trust the view saves it.
        # However, testing with APIFactory/Client sometimes requires session middleware configuration.
        # Given standard Django setup, it should work.

        # We might need to inspect the creation directly if session_id is random.
        assert CartItem.objects.count() == 1
        item = CartItem.objects.first()
        assert item.product == product
        assert item.quantity == 2

    def test_remove_from_cart(self, api_client, product_factory):
        product = product_factory(code="C001")
        url_add = reverse("add-to-cart-api")

        session = api_client.session
        session.create()
        session.save()

        api_client.post(url_add, {"product_code": product.code}, format="json")

        url_remove = reverse("remove-from-cart-api")
        response = api_client.post(
            url_remove, {"product_code": product.code}, format="json"
        )

        assert response.status_code == 200
        assert CartItem.objects.count() == 0

    def test_checkout_flow(self, api_client, product_factory):
        product = product_factory(code="C001", price=100.0)
        url_add = reverse("add-to-cart-api")

        session = api_client.session
        session.create()
        session.save()

        api_client.post(url_add, {"product_code": product.code}, format="json")

        url_checkout = reverse("checkout-api")
        response = api_client.post(
            url_checkout, {"email": "test@example.com"}, format="json"
        )

        assert response.status_code == 200
        assert Order.objects.count() == 1
        order = Order.objects.first()
        assert order.email == "test@example.com"
        assert order.total == 100.0
        assert CartItem.objects.count() == 0  # Cart emptied

    def test_cart_view_contents(self, api_client, product_factory):
        product = product_factory(code="C001")
        url_add = reverse("add-to-cart-api")
        # Ensure session exists
        session = api_client.session
        session.create()
        session.save()
        api_client.post(url_add, {"product_code": product.code}, format="json")

        url_cart = reverse("cart-api")
        response = api_client.get(url_cart)
        assert response.status_code == 200
        assert "image" in response.data["items"][0]
