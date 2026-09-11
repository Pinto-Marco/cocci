from __future__ import annotations
import pytest
from django.conf import settings
from django.test import Client


@pytest.mark.django_db  # CartMiddleware touches the session on every request
def test_media_is_served_with_debug_off():
    """Media used to be wired up only under `if settings.DEBUG:`, so every
    /media/ URL 404'd as soon as DEBUG was turned off for production. Tests run
    with DEBUG=False, so this fails if that ever comes back."""
    assert settings.DEBUG is False
    response = Client().get("/media/images/logo.svg")
    assert response.status_code == 200
