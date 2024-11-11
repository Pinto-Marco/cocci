from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.ProductView.as_view(), name='product'),
    path('delete/', views.ProductDeleteView.as_view(), name='delete-product'),
]

