from django.db import models
from django.core.files import File
from barcode import Code128
from barcode.writer import ImageWriter
from io import BytesIO
from django.utils import timezone

class Product(models.Model):
    code = models.CharField(max_length=16)
    price = models.FloatField(null=True, blank=True)
    title = models.CharField(max_length=15)
    description = models.TextField(null=True, blank=True)
    barcode = models.ImageField(upload_to='uploads/barcodes/', blank=True, null=True)

    def __str__(self):
        return self.code

    def save(self, *args, **kwargs):
        if not self.barcode:
            barcode_image = Code128(self.code, writer=ImageWriter())
            buffer = BytesIO()
            barcode_image.write(buffer)
            file_name = f"{self.code}_barcode.png"
            self.barcode.save(file_name, File(buffer), save=False)
        
        super().save(*args, **kwargs)

    
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='uploads/product_images/')

    def __str__(self):
        return self.product.code
    
class ProductHistory(models.Model):
    ACTION_CHOICES = [
        ('created', 'Created'),
        ('deleted', 'Deleted'),
    ]

    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)  # ForeignKey con SET_NULL
    code = models.CharField(max_length=16, null=True, blank=True)  # Mantiene il codice del prodotto anche se eliminato
    price = models.FloatField(null=True, blank=True)
    title = models.CharField(max_length=15, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        local_timestamp = timezone.localtime(self.timestamp)  # Converte il timestamp in orario locale
        formatted_timestamp = local_timestamp.strftime('%d-%m-%Y %H:%M:%S')  # Formatta la data e ora
        return f"{self.code} - {self.action} - {formatted_timestamp}"