from django.db import models
from product.models import Product

class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    session_id = models.CharField(max_length=255)
    date_added = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.quantity} x {self.product.title}"
    
    @property
    def total_price(self):
        return self.product.price * self.quantity

class Order(models.Model):
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    session_id = models.CharField(max_length=255)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    def __str__(self):
        return f"Order {self.id} - {self.email}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return f"{self.quantity} of {self.product.title}"
    
    @property
    def total_price(self):
        return self.price * self.quantity