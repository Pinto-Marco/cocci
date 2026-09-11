from __future__ import annotations
import pytest
from django.urls import reverse


@pytest.mark.django_db
class TestStoreViewParity:
    """The archive page is a Vue shell (StoreView renders vue_base.html with no
    context) and the listing is fetched client-side from /products/. The old
    tests asserted server-rendered products and had been failing ever since the
    page moved to Vue; they now check the two halves that actually exist."""

    def test_store_view_serves_the_vue_shell(self, client):
        response = client.get(reverse("archive"))
        assert response.status_code == 200
        assert "vue_base.html" in [t.name for t in response.templates]

    def test_products_api_returns_the_product(self, client, product_factory):
        p1 = product_factory(code="1001")

        response = client.get(reverse("product"))
        assert response.status_code == 200
        assert p1.title in str(response.content)
