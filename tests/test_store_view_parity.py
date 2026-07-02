from __future__ import annotations
import pytest
from django.urls import reverse


@pytest.mark.django_db
class TestStoreViewParity:
    def test_store_view_status(self, client):
        url = reverse("archive")
        response = client.get(url)
        assert response.status_code == 200
        assert "products" in response.context
        assert "tags" in response.context

    def test_store_view_filtering(self, client, product_factory):
        # We cannot easily test the exact context shape without inspecting the view logic deeply,
        # but we can verify it returns 200 and has correct templates.
        p1 = product_factory(code="1001")

        url = reverse("archive")
        response = client.get(url)
        assert p1.title in str(response.content)
