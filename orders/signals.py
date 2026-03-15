from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from .models import Order, OrderItem

@receiver(pre_save, sender=Order)
def track_order_confirmation_change(sender, instance, **kwargs):
    if instance.pk:
        previous_order = Order.objects.get(pk=instance.pk)
        instance._previous_confirmed = previous_order.confirmed
    else:
        instance._previous_confirmed = False

@receiver(post_save, sender=Order)
def handle_order_confirmation(sender, instance, created, **kwargs):
    # Handle transition transitions
    previous_confirmed = getattr(instance, '_previous_confirmed', False)
    
    if instance.confirmed and not previous_confirmed:
        # Order just became confirmed: mark products as unavailable
        for item in instance.items.all():
            item.product.is_available = False
            item.product.save()
    elif not instance.confirmed and previous_confirmed:
        # Order was confirmed and now is unconfirmed: mark products as available
        for item in instance.items.all():
            item.product.is_available = True
            item.product.save()

@receiver(post_delete, sender=Order)
def handle_order_deletion(sender, instance, **kwargs):
    # If a confirmed order is deleted, mark its products as available
    if instance.confirmed:
        for item in instance.items.all():
            item.product.is_available = True
            item.product.save()

@receiver(post_delete, sender=OrderItem)
def handle_order_item_deletion(sender, instance, **kwargs):
    # if an item is removed from a confirmed order, mark it as available
    if instance.order.confirmed:
        instance.product.is_available = True
        instance.product.save()
