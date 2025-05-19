from django.urls import path, include
from . import views

urlpatterns = [
    # Product API endpoints
    path('', views.ProductView.as_view(), name='product'),
    #path('delete', views.ProductDeleteView.as_view(), name='delete-product'),
    # path('categories', views.CategoryListView.as_view(), name='categories-details'),
    path('<int:code>/', views.ProductTransferView.as_view(), name='product-transfer'),
    path('details/<int:code>/', views.ProductDetailsUpdateView.as_view(), name='product-details-update'),
]

