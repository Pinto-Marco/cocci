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
    label = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    created_date = models.DateTimeField(auto_now_add=True)
    session_id = models.CharField(max_length=255)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    confirmed = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Order {self.id} - {self.email}"

    def save(self, *args, **kwargs):
        if self.confirmed:
            items = OrderItem.objects.filter(order=self)
            for item in items:
                item.product.is_available = False
                item.product.save()
        super().save(*args, **kwargs)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.product.title}"
    
    @property
    def total_price(self):
        return self.price * self.quantity