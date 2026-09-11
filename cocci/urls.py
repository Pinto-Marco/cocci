"""
URL configuration for cocci project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include, re_path
from django.views.static import serve
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)
from product.views import StoreView, HomeView, ContactsView
from orders.views import OrderConfirmationView

from cocci import settings

urlpatterns = [
    path("admin/", admin.site.urls),
    path("products/", include("product.urls")),
    path("cart/", include("orders.urls")),
    path("", HomeView, name="home"),
    path("archive/", StoreView, name="archive"),
    path("contacts/", ContactsView, name="contacts"),
    path("order-confirmation/", OrderConfirmationView, name="order-confirmation"),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "swagger/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"
    ),
    path(
        "swagger/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"
    ),
]
# Media is served by Django in every mode. This used to be
# `if settings.DEBUG: urlpatterns += static(...)`, and static() is itself a
# no-op when DEBUG is off, so turning DEBUG off 404'd the logo and every
# uploaded image.
# ponytail: django.views.static.serve ties up a worker per file. The upgrade is
# an nginx `location /media/ { alias /home/ec2-user/media/; }` on the host — the
# deploy already mounts that directory — after which this block can go.
urlpatterns += [
    re_path(
        r"^%s(?P<path>.*)$" % settings.MEDIA_URL.lstrip("/"),
        serve,
        {"document_root": settings.MEDIA_ROOT},
    )
]

# lista di tutti i prodotti
# update del prodotto
# is_available
