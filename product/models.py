from django.db import models
from django.core.files import File
from barcode import Code128
from barcode.writer import ImageWriter
from io import BytesIO
from django.utils import timezone

# tag deve stare dentro a product in admi

class Product(models.Model):
    code = models.CharField(max_length=16)
    price = models.FloatField(null=True, blank=True)
    title = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    barcode = models.ImageField(upload_to='uploads/barcodes/', blank=True, null=True)
    penalty = models.FloatField(default=0)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} - {self.code}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    # def get_category(self):
    #     if ProductCategory.objects.filter(product=self).exists():
    #         return ProductCategory.objects.filter(product=self).first().category
        # return None
    
    def get_tags(self):
        return ProductTag.objects.filter(product=self).values_list('tag__name', flat=True)

    
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    # image = models.ImageField(upload_to='uploads/product_images/')
    image = models.CharField(max_length=255)

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
    
# class Category(models.Model):
#     name = models.CharField(max_length=50)

#     def __str__(self):
#         return f"{self.id} - {self.name}"
    
# class ProductCategory(models.Model):
#     product = models.ForeignKey(Product, on_delete=models.CASCADE)
#     category = models.ForeignKey(Category, on_delete=models.CASCADE)

#     def __str__(self):
#         return f"{self.id} - {self.product.code} - {self.category.name}"
    
#     def save(self, *args, **kwargs):
#         if self.product.get_category() is not None:
#             raise ValueError("Il prodotto ha già una categoria associata")
#         super().save(*args, **kwargs)

class Tag(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.id} - {self.name}"
    
class ProductTag(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.id} - {self.product.code} - {self.tag.name}"

_PROXY = "https://wsrv.nl/?url="


def unthumb(url):
    """Recover the S3 original from a proxied URL.

    The mobile app seeds its save payload with the URLs it was served
    (cocci_mobile/lib/utils.dart:132), so without this the proxied URL would be
    written back to the DB and then wrapped a second time.
    """
    if url and url.startswith(_PROXY):
        return "https://" + url[len(_PROXY):].split("&", 1)[0]
    return url


def thumb(url, width=1000):
    """Resize an S3 original through wsrv.nl before it reaches the browser.

    The bucket holds untouched iPhone originals: 3024x3024, ~4MB each. The
    archive grid renders 12 of them at ~350px, so a page used to pull ~50MB.
    At w=1000 the same image is ~290KB.

    ponytail: free third-party proxy, zero infra. The upgrade path is writing
    _<width>.webp derivatives into the bucket at upload time and deleting this.
    """
    url = unthumb(url)
    if not url or not url.startswith("https://"):
        return url
    return f"{_PROXY}{url[len('https://'):]}&w={width}&output=webp&q=80"
