from orders.models import CartItem

class CartMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Code to be executed for each request before the view is called
        if hasattr(request, 'session') and 'cart_id' in request.session:
            session_id = request.session['cart_id']
            cart_items = CartItem.objects.filter(session_id=session_id)
            request.session['cart_items'] = sum(item.quantity for item in cart_items)
        else:
            request.session['cart_items'] = 0

        response = self.get_response(request)
        
        # Code to be executed for each request/response after the view is called
        return response