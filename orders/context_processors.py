from .models import CartItem

def cart_processor(request):
    """
    Context processor that adds cart information to the template context.
    """
    cart_count = 0
    
    if hasattr(request, 'session') and 'cart_id' in request.session:
        session_id = request.session['cart_id']
        cart_items = CartItem.objects.filter(session_id=session_id)
        cart_count = sum(item.quantity for item in cart_items)
    
    return {
        'cart_count': cart_count
    }