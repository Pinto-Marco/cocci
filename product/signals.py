from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Product, ProductHistory

@receiver(post_save, sender=Product)
def create_product_history_on_create(sender, instance, created, **kwargs):
    if created:
        ProductHistory.objects.create(
            product=instance,  # Associa il prodotto come chiave esterna
            code=instance.code,
            price=instance.price,
            title=instance.title,
            description=instance.description,
            action='created'
        )

@receiver(post_delete, sender=Product)
def create_product_history_on_delete(sender, instance, **kwargs):
    ProductHistory.objects.create(
        product=None,  # Imposta il prodotto a NULL
        code=instance.code,
        price=instance.price,
        title=instance.title,
        description=instance.description,
        action='deleted'
    )
