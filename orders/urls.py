from django.urls import path, include
from . import views

urlpatterns = [
    # Product API endpoints
    path('', views.CartView.as_view(), name='cart-api'),
    path('add/', views.AddToCartView.as_view(), name='add-to-cart-api'),
    path('remove/', views.RemoveFromCartView.as_view(), name='remove-from-cart-api'),
    path('make-checkout/', views.CheckoutView.as_view(), name='checkout-api'),
    path('summary/', views.CartPageView, name='summary'),
    path('checkout/', views.CheckoutPageView, name='checkout'),
]




