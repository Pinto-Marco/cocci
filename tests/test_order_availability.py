import pytest
from orders.models import Order, OrderItem
from product.models import Product

@pytest.mark.django_db
class TestOrderAvailabilitySignals:
    
    def test_order_confirmation_marks_unavailable(self, product_factory):
        product = product_factory(code="P1", is_available=True)
        order = Order.objects.create(email="test@example.com")
        OrderItem.objects.create(order=order, product=product, price=product.price)
        
        # Confirm order
        order.confirmed = True
        order.save()
        
        product.refresh_from_db()
        assert product.is_available is False

    def test_order_unconfirmation_marks_available(self, product_factory):
        product = product_factory(code="P2", is_available=False)
        order = Order.objects.create(email="test@example.com", confirmed=True)
        OrderItem.objects.create(order=order, product=product, price=product.price)
        
        # Unconfirm order
        order.confirmed = False
        order.save()
        
        product.refresh_from_db()
        assert product.is_available is True

    def test_confirmed_order_deletion_marks_available(self, product_factory):
        product = product_factory(code="P3", is_available=False)
        order = Order.objects.create(email="test@example.com", confirmed=True)
        OrderItem.objects.create(order=order, product=product, price=product.price)
        
        # Delete confirmed order
        order.delete()
        
        product.refresh_from_db()
        assert product.is_available is True

    def test_unconfirmed_order_deletion_does_not_change_availability(self, product_factory):
        product = product_factory(code="P4", is_available=True)
        order = Order.objects.create(email="test@example.com", confirmed=False)
        OrderItem.objects.create(order=order, product=product, price=product.price)
        
        # Delete unconfirmed order
        order.delete()
        
        product.refresh_from_db()
        assert product.is_available is True

    def test_order_item_removal_from_confirmed_order_marks_available(self, product_factory):
        product = product_factory(code="P5", is_available=False)
        order = Order.objects.create(email="test@example.com", confirmed=True)
        item = OrderItem.objects.create(order=order, product=product, price=product.price)
        
        # Remove item from confirmed order
        item.delete()
        
        product.refresh_from_db()
        assert product.is_available is True

    def test_order_item_removal_from_unconfirmed_order_does_not_change_availability(self, product_factory):
        product = product_factory(code="P6", is_available=True)
        order = Order.objects.create(email="test@example.com", confirmed=False)
        item = OrderItem.objects.create(order=order, product=product, price=product.price)
        
        # Remove item from unconfirmed order
        item.delete()
        
        product.refresh_from_db()
        assert product.is_available is True
