from django.urls import path, include
from . import views

urlpatterns = [
    # Product API endpoints
    path("", views.ProductView.as_view(), name="product"),
    path("search/", views.ProductSearchView.as_view(), name="product-search"),
    path("tags/", views.TagListView.as_view(), name="tag-list"),
    path("<int:code>/", views.ProductTransferView.as_view(), name="product-transfer"),
    # path('categories', views.CategoryListView.as_view(), name='categories-details'),
    path("<int:code>/", views.ProductTransferView.as_view(), name="product-transfer"),
    # API
    path(
        "api/details/<int:code>/",
        views.ProductDetailsUpdateView.as_view(),
        name="product-details-api",
    ),
    # Vue Page
    path(
        "details/<int:code>/",
        views.ProductDetailPageView,
        name="product-details-page",
    ),
]
