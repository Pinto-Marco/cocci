from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def send_order_emails(order):
    """
    Invia:
    - email di conferma al cliente
    - email di notifica al proprietario del sito
    """

    # --- Email cliente ---
    customer_subject = f"Conferma ordine #{order.id}"
    customer_html = render_to_string("emails/order_confirmation.html", {
        "order": order,
    })
    customer_text = strip_tags(customer_html)

    send_mail(
        subject=customer_subject,
        message=customer_text,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[order.email],
        html_message=customer_html,
        fail_silently=False,
    )

    # --- Email proprietario ---
    owner_subject = f"Nuovo ordine ricevuto #{order.id}"
    owner_html = render_to_string("emails/order_notification.html", {
        "order": order,
    })
    owner_text = strip_tags(owner_html)

    send_mail(
        subject=owner_subject,
        message=owner_text,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[settings.SHOP_OWNER_EMAIL],
        html_message=owner_html,
        fail_silently=False,
    )