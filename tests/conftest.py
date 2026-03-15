import pytest
from rest_framework.test import APIClient
from product.models import Product, Tag, ProductTag


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def product_factory(db):
    def create_product(**kwargs):
        defaults = {
            "code": "1001",
            "title": "Test Product",
            "price": 10.0,
            "description": "A test product",
            "is_available": True,
        }
        defaults.update(kwargs)
        return Product.objects.create(**defaults)

    return create_product
