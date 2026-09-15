import pytest

from product.models import Product, ProductImage

S3 = "https://cocciphoto.s3.eu-central-1.amazonaws.com/cocciphoto"

# The exact payload cocci_mobile/lib/utils.dart:82 posts.
PAYLOAD = {
    "code": "1758000000000",
    "title": "Giacca",
    "description": "Vintage",
    "uploaded_images": [f"{S3}/1758000000000_0.png", f"{S3}/1758000000000_1.png"],
    "tags": ["denim", "80s"],
    "price": "120.0",
    "penalty": "10.0",
    "is_available": True,
}


@pytest.mark.django_db
def test_app_can_create_product_with_tags_and_images(api_client):
    res = api_client.post("/products/", PAYLOAD, format="json")

    assert res.status_code == 201, res.data
    product = Product.objects.get(code=PAYLOAD["code"])
    assert sorted(product.get_tags()) == ["80s", "denim"]
    assert ProductImage.objects.filter(product=product).count() == 2
    # Originals stay in the DB; only the response is proxied.
    assert ProductImage.objects.filter(product=product, image__startswith=S3).count() == 2
    assert all(i["image"].startswith("https://wsrv.nl/?url=") for i in res.data["images"])


@pytest.mark.django_db
def test_saving_echoed_proxy_urls_does_not_double_wrap(api_client):
    """The app re-posts the URLs it was served (utils.dart:132)."""
    created = api_client.post("/products/", PAYLOAD, format="json")
    echoed = [i["image"] for i in created.data["images"]]

    res = api_client.post("/products/", {**PAYLOAD, "code": "1758000000001", "uploaded_images": echoed}, format="json")

    assert res.status_code == 201, res.data
    stored = ProductImage.objects.filter(product__code="1758000000001").values_list("image", flat=True)
    assert all(u.startswith(S3) for u in stored), stored


@pytest.mark.django_db
def test_app_save_and_delete_need_auth_and_hit_the_lookup_route(api_client, product_factory, django_user_model):
    """The routes cocci_mobile now calls: products/lookup/<code>/ (POST, DELETE).

    They used to point at products/details/<code>/, the Vue page, which
    answered 200 text/html and changed nothing.
    """
    product_factory(code="1001", title="Vecchio")
    payload = {**PAYLOAD, "code": "1001", "title": "Nuovo"}

    assert api_client.post("/products/lookup/1001/", payload, format="json").status_code == 403

    django_user_model.objects.create_user(username="app", password="pw")
    api_client.force_authenticate(django_user_model.objects.get(username="app"))

    res = api_client.post("/products/lookup/1001/", payload, format="json")
    assert res.status_code == 201, res.data
    assert Product.objects.get(code="1001").title == "Nuovo"

    assert api_client.delete("/products/lookup/1001/").status_code == 200
    assert not Product.objects.filter(code="1001").exists()


@pytest.mark.django_db
def test_basic_auth_header_is_accepted(api_client, product_factory, django_user_model):
    """cocci_mobile sends `Authorization: Basic ...` (lib/utils.dart api())."""
    import base64

    product_factory(code="1002")
    django_user_model.objects.create_user(username="app", password="pw")
    token = base64.b64encode(b"app:pw").decode()

    res = api_client.post(
        "/products/lookup/1002/",
        {**PAYLOAD, "code": "1002", "title": "Via Basic"},
        format="json",
        HTTP_AUTHORIZATION=f"Basic {token}",
    )

    assert res.status_code == 201, res.data
    assert Product.objects.get(code="1002").title == "Via Basic"


@pytest.mark.django_db
def test_app_account_needs_no_staff_flag_and_cannot_reach_admin(api_client, product_factory, django_user_model):
    """L'account dedicato all'app: puo' scrivere, non puo' entrare in /admin/."""
    import base64

    product_factory(code="1003")
    user = django_user_model.objects.create_user("cocci-app", password="pw")
    assert not user.is_staff and not user.is_superuser
    token = base64.b64encode(b"cocci-app:pw").decode()

    res = api_client.post(
        "/products/lookup/1003/",
        {**PAYLOAD, "code": "1003", "title": "Salvato dall'app"},
        format="json",
        HTTP_AUTHORIZATION=f"Basic {token}",
    )
    assert res.status_code == 201, res.data

    api_client.login(username="cocci-app", password="pw")
    admin = api_client.get("/admin/", follow=True)
    assert admin.resolver_match.url_name == "login"
    assert b"not authorized to access this page" in admin.content
