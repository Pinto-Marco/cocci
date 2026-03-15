from __future__ import annotations
import pytest
from django.urls import reverse


@pytest.mark.django_db
class TestProductAPI:
    def test_get_product_list(self, api_client, product_factory):
        product1 = product_factory(code="P001", title="Product 1", price=10.0)
        product2 = product_factory(code="P002", title="Product 2", price=20.0)

        url = reverse("product")
        response = api_client.get(url)

        assert response.status_code == 200
        assert response.data["count"] == 2
        assert len(response.data["results"]) == 2

    def test_filter_by_tag(self, api_client, product_factory):
        # Setup
        p1 = product_factory(code="P001", title="Tagged Product")
        p2 = product_factory(code="P002", title="Untagged Product")

        from product.models import Tag, ProductTag

        tag = Tag.objects.create(name="sale")
        ProductTag.objects.create(product=p1, tag=tag)

        # Test
        url = reverse("product")
        response = api_client.get(url, {"tags": tag.id})

        assert response.status_code == 200
        assert response.data["count"] == 1
        assert response.data["results"][0]["code"] == "P001"

    def test_sort_by_price(self, api_client, product_factory):
        p1 = product_factory(code="1001", price=20.0)
        p2 = product_factory(code="1002", price=10.0)

        url = reverse("product")

        # Ascending
        resp_asc = api_client.get(url, {"order_by_price": "asc"})
        assert resp_asc.data["results"][0]["code"] == "1002"
        # Descending
        resp_desc = api_client.get(url, {"order_by_price": "desc"})
        assert resp_desc.data["results"][0]["code"] == "1001"

    def test_sort_by_year(self, api_client, product_factory):
        # code is "year" proxy
        p1 = product_factory(code="2020", price=10.0)
        p2 = product_factory(code="2021", price=10.0)

        url = reverse("product")

        # Ascending (Oldest first)
        resp_asc = api_client.get(url, {"sort": "year_asc"})
        assert resp_asc.data["results"][0]["code"] == "2020"

        # Descending (Newest first)
        resp_desc = api_client.get(url, {"sort": "year_desc"})
        assert resp_desc.data["results"][0]["code"] == "2021"

    def test_search_by_title(self, api_client, product_factory):
        product_factory(code="P100", title="Silk Dress", description="Evening piece")
        product_factory(code="P101", title="Linen Shirt", description="Casual")

        url = reverse("product-search")
        response = api_client.get(url, {"q": "silk"})

        assert response.status_code == 200
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["code"] == "P100"

    def test_search_by_description(self, api_client, product_factory):
        product_factory(
            code="P200", title="Classic Blazer", description="Perfect for weddings"
        )
        product_factory(code="P201", title="Summer Skirt", description="Beach style")

        url = reverse("product-search")
        response = api_client.get(url, {"q": "weddings"})

        assert response.status_code == 200
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["code"] == "P200"

    def test_search_relevance_prioritizes_title_start(
        self, api_client, product_factory
    ):
        product_factory(code="P300", title="Velvet Coat", description="Warm")
        product_factory(code="P301", title="Coat Dress", description="Formal")
        product_factory(
            code="P302", title="Trench", description="A smart coat for spring"
        )

        url = reverse("product-search")
        response = api_client.get(url, {"q": "coat"})

        assert response.status_code == 200
        assert response.data["results"][0]["code"] == "P301"

    def test_search_payload_is_lightweight(self, api_client, product_factory):
        product_factory(code="P400", title="Wool Pants", description="Tailored")

        url = reverse("product-search")
        response = api_client.get(url, {"q": "wool"})

        assert response.status_code == 200
        assert len(response.data["results"]) == 1
        result = response.data["results"][0]
        assert set(result.keys()) == {"code", "title", "description", "is_available"}
